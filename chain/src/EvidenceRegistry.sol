// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract EvidenceRegistry is EIP712, Ownable {
    bytes32 public constant EVIDENCE_TYPEHASH =
        keccak256("Evidence(bytes32 eventId,bytes32 payloadHash,bytes32 previousHash,uint8 eventType)");

    struct Record {
        bytes32 payloadHash;
        bytes32 previousHash;
        uint8 eventType;
        address signer;
        uint64 recordedAt;
    }

    mapping(address => bool) public authorizedSigners;
    mapping(bytes32 => Record) public records;

    event SignerAuthorizationChanged(address indexed signer, bool authorized);
    event EvidenceRecorded(
        bytes32 indexed eventId, bytes32 payloadHash, bytes32 previousHash, uint8 eventType, address indexed signer
    );

    constructor(address initialOwner) EIP712("LamToEvidence", "1") Ownable(initialOwner) {}

    function setAuthorizedSigner(address signer, bool authorized) external onlyOwner {
        require(signer != address(0), "zero signer");
        authorizedSigners[signer] = authorized;
        emit SignerAuthorizationChanged(signer, authorized);
    }

    function hashEvidence(bytes32 eventId, bytes32 payloadHash, bytes32 previousHash, uint8 eventType)
        public
        view
        returns (bytes32)
    {
        return _hashTypedDataV4(keccak256(abi.encode(EVIDENCE_TYPEHASH, eventId, payloadHash, previousHash, eventType)));
    }

    function recordEvidence(
        bytes32 eventId,
        bytes32 payloadHash,
        bytes32 previousHash,
        uint8 eventType,
        address signer,
        bytes calldata signature
    ) external {
        require(eventId != bytes32(0), "zero event");
        require(payloadHash != bytes32(0), "zero payload");
        require(eventType >= 1 && eventType <= 11, "unknown event type");
        require(records[eventId].recordedAt == 0, "duplicate event");
        require(authorizedSigners[signer], "unauthorized signer");
        require(
            ECDSA.recover(hashEvidence(eventId, payloadHash, previousHash, eventType), signature) == signer,
            "bad signature"
        );
        records[eventId] = Record(payloadHash, previousHash, eventType, signer, uint64(block.timestamp));
        emit EvidenceRecorded(eventId, payloadHash, previousHash, eventType, signer);
    }
}
