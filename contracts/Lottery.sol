// SPDX-License-Identifier: MIT

// Smart contract that lets anyone deposit ETH into the contract
// Only the owner of the contract can withdraw the ETH
pragma solidity ^0.8.12;

// Get the latest ETH/USD price from chainlink price feed
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

contract Lottery is VRFConsumerBaseV2 {
    VRFCoordinatorV2Interface COORDINATOR;
    uint64 s_subscriptionId;
    bytes32 keyHash;
    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;

    uint256[] public s_randomWords;
    uint256 s_requestId;

    AggregatorV3Interface priceFeed;
    mapping(address => uint256) public participantsMap;
    uint256 priceTicketUSD;
    address[] participants;

    address private owner;
    uint256 public winnerIndex;

    event ClosingLottery(uint256 s_requestId);

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE lotteryState;

    constructor(
        address _priceFeed,
        uint256 _priceTicketUSD,
        bytes32 _keyhash,
        address _vrfCoordinator
    ) public VRFConsumerBaseV2(_vrfCoordinator) {
        COORDINATOR = VRFCoordinatorV2Interface(_vrfCoordinator);
        keyHash = _keyhash;
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
        priceTicketUSD = _priceTicketUSD * (10**18);
        lotteryState = LOTTERY_STATE.CLOSED;
    }

    function openLottery() public onlyOwner {
        lotteryState = LOTTERY_STATE.OPEN;
    }

    function closeLottery() public onlyOwner {
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
        requestRandomWords();
        emit ClosingLottery(s_requestId);
    }

    function getTicketFeeETH() public view returns (uint256) {
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        return (priceTicketUSD * precision) / price;
    }

    function buyLotteryTicket() public payable {
        require(
            msg.value >= getTicketFeeETH(),
            "You need to spend more ETH to buy a ticket"
        );
        require(lotteryState == LOTTERY_STATE.OPEN, "Lottery is not open");
        participantsMap[msg.sender] += msg.value;
        participants.push(msg.sender);
    }

    function getMyLotteryTicketsNbr() public view returns (uint256) {
        address participant = msg.sender;
        uint256 ticketsNbr = 0;
        return (participantsMap[msg.sender] / getTicketFeeETH());
    }

    // Chainlink helpers
    function getPrice() private view returns (uint256) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        // ETH/USD rate in 18 digit
        return uint256(answer) * (10**10);
    }

    // VRFV2 helpers
    function setSubscription(uint64 _subId) public onlyOwner {
        s_subscriptionId = _subId;
    }

    function requestRandomWords() private onlyOwner {
        require(s_subscriptionId != 0, "Subscription ID is not set");
        s_requestId = COORDINATOR.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
    }

    function fulfillRandomWords(
        uint256, /* requestId */
        uint256[] memory randomWords
    ) internal override {
        s_randomWords = randomWords;
        winnerIndex = s_randomWords[0] % participants.length;
        payable(participants[winnerIndex]).transfer(address(this).balance);
        participants = new address[](0);
        for (
            uint256 funderIndex = 0;
            funderIndex < participants.length;
            funderIndex++
        ) {
            address funder = participants[funderIndex];
            participantsMap[funder] = 0;
        }
        lotteryState = LOTTERY_STATE.CLOSED;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
}
