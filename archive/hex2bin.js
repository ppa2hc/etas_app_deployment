#!/usr/bin/env node

const fs = require('fs');
const intelHex = require('intel-hex');

function parseAddress(addrStr) {
  const addr = Number(addrStr);
  if (isNaN(addr)) {
    if (addrStr.startsWith('0x') || addrStr.startsWith('0X')) {
      return parseInt(addrStr, 16);
    }
    throw new Error(`Invalid address: ${addrStr}`);
  }
  return addr;
}

function usage() {
  console.log('Usage: node hex2bin.js <input_hex> <start_address> <end_address> <output_bin>');
  process.exit(1);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length !== 4) {
    usage();
  }

  const [inputHexPath, startAddressStr, endAddressStr, outputBinPath] = args;

  try {
    const startAddr = parseAddress(startAddressStr);
    const endAddr = parseAddress(endAddressStr);

    if (startAddr > endAddr) {
      console.error('Error: Start address must be less than or equal to end address.');
      process.exit(1);
    }

    const hexContent = fs.readFileSync(inputHexPath, 'utf8');
    const parsed = intelHex.parse(hexContent);

    const baseAddr = parsed.startAddress || 0;
    const length = endAddr - startAddr;
    if (length <= 0) {
      console.error('Error: End address must be greater than start address.');
      process.exit(1);
    }

    const outputBuffer = Buffer.alloc(length, 0);

    const dataStart = baseAddr;
    const dataEnd = baseAddr + parsed.data.length;

    const copyStart = Math.max(startAddr, dataStart);
    const copyEnd = Math.min(endAddr, dataEnd);

    if (copyEnd > copyStart) {
      const sourceStartIndex = copyStart - dataStart;
      const destStartIndex = copyStart - startAddr;
      const bytesToCopy = copyEnd - copyStart;

      parsed.data.copy(outputBuffer, destStartIndex, sourceStartIndex, sourceStartIndex + bytesToCopy);
    }

    fs.writeFileSync(outputBinPath, outputBuffer);
    console.log(`Successfully wrote binary file: ${outputBinPath}`);

  } catch (err) {
    console.error('Error:', err.message || err);
    process.exit(1);
  }
}

main();
