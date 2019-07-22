import binascii

try:
    from hashlib import blake2s
except:
    from pyblake2 import blake2s
blake = lambda x: blake2s(x).digest()

def merkelize(L):
    # L = permute4(L)
    nodes = [b''] * len(L) + [x.to_bytes(32, 'big') if isinstance(x, int) else x for x in L]
    for i in range(len(L) - 1, 0, -1):
        nodes[i] = blake(nodes[i*2] + nodes[i*2+1])

    return nodes

def mk_branch(tree, index):
    # index = get_index_in_permuted(index, len(tree) // 2)
    index += len(tree) // 2
    o = [tree[index]]
    while index > 1:
        o.append(tree[index ^ 1])
        index //= 2
    return o

def verify_branch(root, index, proof, output_as_int=False):
    # index = get_index_in_permuted(index, 2**len(proof) // 2)
    print("pow part is ", str(2**len(proof)))
    print("idx is ", str(index))
    index += 2**len(proof)
    print("index is " + str(index))
    v = proof[0]
    for p in proof[1:]:
        if index % 2:
            print("left")
            v = blake(p + v)
            print("res is ")
            print(binascii.hexlify(v))
        else:
            print("right")
            v = blake(v + p)
            print("res is ")
            print(binascii.hexlify(v))
        index //= 2
    assert v == root
    # import pdb; pdb.set_trace()
    return int.from_bytes(proof[0], 'big') if output_as_int else proof[0]

# Make a compressed proof for multiple indices
def mk_multi_branch(tree, indices):
    # Branches we are outputting
    output = []
    # Elements in the tree we can get from the branches themselves
    calculable_indices = {}
    for i in indices:
        new_branch = mk_branch(tree, i)
        index = len(tree) // 2 + i
        calculable_indices[index] = True
        for j in range(1, len(new_branch)):
            calculable_indices[index ^ 1] = True
            index //= 2
        output.append(new_branch)
    return output

# Verify a compressed proof
def verify_multi_branch(root, indices, proof):
    # The values in the Merkle tree we can fill in
    partial_tree = {}
    # Fill in elements from the branches
    for i, b in zip(indices, proof):
        half_tree_size = 2**(len(b) - 1)
        index = half_tree_size+i
        partial_tree[index] = b[0]
        for j in range(1, len(b)):
            if b[j]:
                partial_tree[index ^ 1] = b[j]
            index //= 2
    # Verify the branches and output the values
    output = []
    for i,b in zip(indices, proof):
        output.append(verify_branch(root, i, b))

    return output
    # return [verify_branch(root, i, b) for i,b in zip(indices, proof)]

# Byte length of a multi proof
def bin_length(proof):
    return sum([len(b''.join(x)) + len(x) // 8 for x in proof]) + len(proof) * 2
