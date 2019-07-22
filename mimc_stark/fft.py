def _simple_ft(vals, modulus, roots_of_unity):
    L = len(roots_of_unity)
    o = []
    for i in range(L):
        last = 0
        for j in range(L):
            last += vals[j] * roots_of_unity[(i*j)%L]
        o.append(last % modulus)
    return o

def _fft(vals, modulus, roots_of_unity):
    if len(vals) <= 4:
        #return vals
        return _simple_ft(vals, modulus, roots_of_unity)
    L = _fft(vals[::2], modulus, roots_of_unity[::2])
    R = _fft(vals[1::2], modulus, roots_of_unity[::2])
    # print("L is ", L)
    # print("R is ", R)

    o = [0 for i in vals]
    for i, (x, y) in enumerate(zip(L, R)):
        y_times_root = y*roots_of_unity[i]
        o[i] = (x+y_times_root) % modulus 
        # print("o[i] = ", o[i])
        o[i+len(L)] = (x-y_times_root) % modulus 
        # print("o[i+Len(L)] = ", o[i+len(L)])
        # print("modulus = ", modulus)
        # print("x-y_times_root ", x-y_times_root)
        # print("(x-y_times_root) % modulus", (x-y_times_root) % modulus)

    return o

def fft(vals, modulus, root_of_unity, inv=False):
    # Build up roots of unity
    rootz = [1, root_of_unity]
    while rootz[-1] != 1:
        rootz.append((rootz[-1] * root_of_unity) % modulus)
    # Fill in vals with zeroes if needed
    if len(rootz) > len(vals) + 1:
        vals = vals + [0] * (len(rootz) - len(vals) - 1)
    if inv:
        # Inverse FFT
        # println("len vals ", len(vals))
        # println("modulus ", modulus)
        invlen = pow(len(vals), modulus-2, modulus)
        # print("invlen is ", invlen)
        fft_res = _fft(vals, modulus, rootz[:0:-1])
        res = [(x*invlen) % modulus for x in fft_res]
        # print("final result is ", res)
        return res
    else:
        # Regular FFT
        return _fft(vals, modulus, rootz[:-1])

def mul_polys(a, b, modulus, root_of_unity):
    rootz = [1, root_of_unity]
    while rootz[-1] != 1:
        rootz.append((rootz[-1] * root_of_unity) % modulus)
    if len(rootz) > len(a) + 1:
        a = a + [0] * (len(rootz) - len(a) - 1)
    if len(rootz) > len(b) + 1:
        b = b + [0] * (len(rootz) - len(b) - 1)
    x1 = _fft(a, modulus, rootz[:-1])
    x2 = _fft(b, modulus, rootz[:-1])
    return _fft([(v1*v2)%modulus for v1,v2 in zip(x1,x2)],
               modulus, rootz[:0:-1])
