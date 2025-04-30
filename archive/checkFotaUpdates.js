const fs = require('fs');
const path = require('path');

const folderPath = '/media/sf_C_DRIVE/Users/ppa2hc/etas_ota/fota';
const snapshotFile = './fota_snapshot.json';
const checkIntervalMs = 5 * 1000; // 10 seconds

// Recursively get all files with their stats
function getFilesRecursive(dir) {
  let results = {};
  const list = fs.readdirSync(dir);

  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      const subFiles = getFilesRecursive(filePath);
      results = { ...results, ...subFiles };
    } else {
      results[filePath] = {
        mtimeMs: stat.mtimeMs,
        size: stat.size,
      };
    }
  });

  return results;
}

// Load previous snapshot or empty object
function loadSnapshot() {
  if (fs.existsSync(snapshotFile)) {
    try {
      return JSON.parse(fs.readFileSync(snapshotFile, 'utf8'));
    } catch (err) {
      console.error('Failed to parse snapshot file:', err);
      // Return empty object to avoid crash
    }
  }
  return {};
}

// Save current snapshot to file
function saveSnapshot(snapshot) {
  try {
    fs.writeFileSync(snapshotFile, JSON.stringify(snapshot, null, 2));
  } catch (err) {
    console.error('Failed to save snapshot:', err);
  }
}

// Compare snapshots and report changes
function compareSnapshots(oldSnap, newSnap) {
  const added = [];
  const modified = [];
  const deleted = [];

  for (const file in newSnap) {
    if (!oldSnap[file]) {
      added.push(file);
    } else if (
      oldSnap[file].mtimeMs !== newSnap[file].mtimeMs ||
      oldSnap[file].size !== newSnap[file].size
    ) {
      modified.push(file);
    }
  }

  for (const file in oldSnap) {
    if (!newSnap[file]) {
      deleted.push(file);
    }
  }

  return { added, modified, deleted };
}

// Check for updates and print changes
function checkForUpdates() {
  const oldSnapshot = loadSnapshot();
  const newSnapshot = getFilesRecursive(folderPath);
  const changes = compareSnapshots(oldSnapshot, newSnapshot);

  if (
    changes.added.length === 0 &&
    changes.modified.length === 0 &&
    changes.deleted.length === 0
  ) {
    console.log(new Date().toLocaleTimeString(), '- No changes detected.');
  } else {
    if (changes.added.length > 0) {
      console.log(new Date().toLocaleTimeString(), '- Added files:');
      changes.added.forEach(f => console.log('  +', f));
    }
    if (changes.modified.length > 0) {
      console.log(new Date().toLocaleTimeString(), '- Modified files:');
      changes.modified.forEach(f => console.log('  *', f));
    }
    if (changes.deleted.length > 0) {
      console.log(new Date().toLocaleTimeString(), '- Deleted files:');
      changes.deleted.forEach(f => console.log('  -', f));
    }
  }

  saveSnapshot(newSnapshot);
}

// Sleep helper
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Main program entry point
async function main() {
  console.log('Starting folder monitor for:', folderPath);
  console.log(`Checking every ${checkIntervalMs / 1000} seconds.`);

  // Handle graceful shutdown on Ctrl+C
  process.on('SIGINT', () => {
    console.log('\nReceived SIGINT. Exiting...');
    process.exit(0);
  });

  try {
    while (true) {
      checkForUpdates();
      await sleep(checkIntervalMs);
    }
  } catch (err) {
    console.error('Fatal error:', err);
    process.exit(1);
  }
}

// Execute main if this file is run directly
if (require.main === module) {
  main();
}
