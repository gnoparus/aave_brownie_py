// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.6.12;

// https://github.com/aave/protocol-v2/blob/master/contracts/misc/interfaces/IWETH.sol
interface IWETH {
    function deposit() external payable;

    function withdraw(uint256) external;

    function approve(address guy, uint256 wad) external returns (bool);

    function transferFrom(
        address src,
        address dst,
        uint256 wad
    ) external returns (bool);
}
