// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import {Script, console2} from "forge-std/Script.sol";
import {EvidenceRegistry} from "../src/EvidenceRegistry.sol";

contract DeployEvidenceRegistry is Script {
    function run() external returns (EvidenceRegistry registry) {
        address owner = vm.envAddress("OWNER_ADDRESS");
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerKey);
        registry = new EvidenceRegistry(owner);
        vm.stopBroadcast();

        console2.log("EvidenceRegistry deployed at:", address(registry));
        console2.log("Owner:", owner);
    }
}
