// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import {Test} from "forge-std/Test.sol";
import {EvidenceRegistry} from "../src/EvidenceRegistry.sol";

contract EvidenceRegistryTest is Test {
    EvidenceRegistry internal registry;

    uint256 internal signerKey = 0xA11CE;
    address internal signer;
    address internal owner = address(this);

    function setUp() public {
        signer = vm.addr(signerKey);
        registry = new EvidenceRegistry(owner);
        registry.setAuthorizedSigner(signer, true);
    }

    function _signEvidence(bytes32 eventId, bytes32 payloadHash, bytes32 previousHash, uint8 eventType, uint256 key)
        internal
        view
        returns (bytes memory)
    {
        bytes32 digest = registry.hashEvidence(eventId, payloadHash, previousHash, eventType);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(key, digest);
        return abi.encodePacked(r, s, v);
    }

    function testRecordsOneAuthorizedEvidenceEvent() public {
        bytes32 eventId = keccak256("event-1");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes32 previousHash = bytes32(0);
        bytes32 digest = registry.hashEvidence(eventId, payloadHash, previousHash, 1);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(signerKey, digest);
        bytes memory signature = abi.encodePacked(r, s, v);

        registry.recordEvidence(eventId, payloadHash, previousHash, 1, signer, signature);
        (bytes32 storedHash, bytes32 storedPrevious, uint8 storedType, address storedSigner, uint64 recordedAt) =
            registry.records(eventId);

        assertEq(storedHash, payloadHash);
        assertEq(storedPrevious, previousHash);
        assertEq(storedType, 1);
        assertEq(storedSigner, signer);
        assertGt(recordedAt, 0);
    }

    function testRejectsUnauthorizedSigner() public {
        uint256 otherKey = 0xB0B;
        address other = vm.addr(otherKey);
        bytes32 eventId = keccak256("event-unauth");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes memory signature = _signEvidence(eventId, payloadHash, bytes32(0), 1, otherKey);

        vm.expectRevert(bytes("unauthorized signer"));
        registry.recordEvidence(eventId, payloadHash, bytes32(0), 1, other, signature);
    }

    function testRejectsAlteredPayload() public {
        bytes32 eventId = keccak256("event-altered");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes32 alteredHash = sha256(bytes("tampered"));
        bytes memory signature = _signEvidence(eventId, payloadHash, bytes32(0), 1, signerKey);

        vm.expectRevert(bytes("bad signature"));
        registry.recordEvidence(eventId, alteredHash, bytes32(0), 1, signer, signature);
    }

    function testRejectsDuplicateEventId() public {
        bytes32 eventId = keccak256("event-dup");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes memory signature = _signEvidence(eventId, payloadHash, bytes32(0), 1, signerKey);

        registry.recordEvidence(eventId, payloadHash, bytes32(0), 1, signer, signature);

        bytes memory signature2 = _signEvidence(eventId, payloadHash, bytes32(0), 2, signerKey);
        vm.expectRevert(bytes("duplicate event"));
        registry.recordEvidence(eventId, payloadHash, bytes32(0), 2, signer, signature2);
    }

    function testRejectsZeroEventId() public {
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes memory signature = _signEvidence(bytes32(0), payloadHash, bytes32(0), 1, signerKey);

        vm.expectRevert(bytes("zero event"));
        registry.recordEvidence(bytes32(0), payloadHash, bytes32(0), 1, signer, signature);
    }

    function testRejectsZeroPayloadHash() public {
        bytes32 eventId = keccak256("event-zero-payload");
        bytes memory signature = _signEvidence(eventId, bytes32(0), bytes32(0), 1, signerKey);

        vm.expectRevert(bytes("zero payload"));
        registry.recordEvidence(eventId, bytes32(0), bytes32(0), 1, signer, signature);
    }

    function testRejectsUnknownEventTypeZero() public {
        bytes32 eventId = keccak256("event-type-0");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes memory signature = _signEvidence(eventId, payloadHash, bytes32(0), 0, signerKey);

        vm.expectRevert(bytes("unknown event type"));
        registry.recordEvidence(eventId, payloadHash, bytes32(0), 0, signer, signature);
    }

    function testRejectsUnknownEventTypeAboveEleven() public {
        bytes32 eventId = keccak256("event-type-12");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes memory signature = _signEvidence(eventId, payloadHash, bytes32(0), 12, signerKey);

        vm.expectRevert(bytes("unknown event type"));
        registry.recordEvidence(eventId, payloadHash, bytes32(0), 12, signer, signature);
    }

    function testAcceptsEventTypeEleven() public {
        bytes32 eventId = keccak256("event-type-11");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes memory signature = _signEvidence(eventId, payloadHash, bytes32(0), 11, signerKey);

        registry.recordEvidence(eventId, payloadHash, bytes32(0), 11, signer, signature);
        (,, uint8 storedType,,) = registry.records(eventId);
        assertEq(storedType, 11);
    }

    function testExistingRecordReadable() public {
        bytes32 eventId = keccak256("event-readable");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes32 previousHash = keccak256("prior");
        bytes memory signature = _signEvidence(eventId, payloadHash, previousHash, 3, signerKey);

        vm.warp(1_700_000_000);
        registry.recordEvidence(eventId, payloadHash, previousHash, 3, signer, signature);

        (bytes32 storedHash, bytes32 storedPrevious, uint8 storedType, address storedSigner, uint64 recordedAt) =
            registry.records(eventId);
        assertEq(storedHash, payloadHash);
        assertEq(storedPrevious, previousHash);
        assertEq(storedType, 3);
        assertEq(storedSigner, signer);
        assertEq(recordedAt, 1_700_000_000);
    }

    function testOnlyOwnerCanAuthorizeSigner() public {
        address stranger = address(0xBEEF);
        vm.prank(stranger);
        vm.expectRevert();
        registry.setAuthorizedSigner(address(0xCAFE), true);
    }

    function testRejectsZeroSignerAuthorization() public {
        vm.expectRevert(bytes("zero signer"));
        registry.setAuthorizedSigner(address(0), true);
    }

    function testDeauthorizedSignerRejected() public {
        bytes32 eventId = keccak256("event-deauth");
        bytes32 payloadHash = sha256(bytes("payload"));
        bytes memory signature = _signEvidence(eventId, payloadHash, bytes32(0), 1, signerKey);

        registry.setAuthorizedSigner(signer, false);
        vm.expectRevert(bytes("unauthorized signer"));
        registry.recordEvidence(eventId, payloadHash, bytes32(0), 1, signer, signature);
    }
}
