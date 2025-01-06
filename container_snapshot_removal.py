import json

import subprocess

def get_all_snapshots():
    try:
        # Execute the `ctr snapshots list` command and capture the output
        result = subprocess.run(['ctr', 'snapshots', 'list'], capture_output=True,
                                text=True)

        # Check if the command executed successfully
        if result.returncode != 0:
            print(f"Error executing command: {result.stderr}")
            return []

        # Split the output into lines and skip the header
        snapshots = result.stdout.splitlines()[1:]
        return [line.split()[0] for line in snapshots]  # Extract snapshot IDs

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_active_snapshots():
    try:
        # Execute the `ctr snapshots list` command and capture the output
        result = subprocess.run(['ctr', 'snapshots', 'list'], capture_output=True,
                                text=True)

        # Check if the command executed successfully
        if result.returncode != 0:
            print(f"Error executing command: {result.stderr}")
            return []

        # Split the output into lines and skip the header
        snapshots = result.stdout.splitlines()[1:]
        active_snapshots = []
        for line in snapshots:
            if 'Active' in line and 'overlayfs' not in line:
                active_snapshots.append(line)
        return [line.split()[0] for line in active_snapshots]  # Extract snapshot IDs

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_snapshot_info(snapshot_id):
    try:
        # Execute the `ctr snapshots info` command to get snapshot metadata
        result = subprocess.run(['ctr', 'snapshots', 'info', snapshot_id],
                                capture_output=True, text=True)

        # Check if the command executed successfully
        if result.returncode != 0:
            print(f"Error fetching info for snapshot {snapshot_id}: {result.stderr}")
            return None

        # Parse the output line by line to extract parent information
        data = json.loads(result.stdout)

        return data

    except Exception as e:
        print(f"An error occurred while getting info for snapshot {snapshot_id}: {e}")
        return None


def build_snapshot_tree():
    snapshots = get_all_snapshots()

    snapshot_tree = {}

    for snapshot_id in snapshots:
        snapshot_info = get_snapshot_info(snapshot_id)
        if snapshot_info and "Parent" in snapshot_info:
            parent_id = snapshot_info["Parent"]
            if parent_id not in snapshot_tree:
                snapshot_tree[parent_id] = []
            snapshot_tree[parent_id].append(snapshot_id)

    return snapshot_tree


def find_last_child(snapshot_tree, snapshot_id):
    # If the snapshot has no children, it's the last child
    if snapshot_id not in snapshot_tree:
        return snapshot_id

    # Recursively find the last child in the subtree
    last_child = snapshot_tree[snapshot_id][-1]  # Get the last child in the list
    return find_last_child(snapshot_tree, last_child)

# Main execution
snapshot_tree = build_snapshot_tree()

# Choose a root snapshot to start from, or iterate through all roots (snapshots with no parent)
roots = [snapshot for snapshot in snapshot_tree.keys() if
         snapshot not in [child for children in snapshot_tree.values() for child in children]]

for root in roots:
    last_child = find_last_child(snapshot_tree, root)
    print(f"Last child of snapshot {root} is: {last_child}")
