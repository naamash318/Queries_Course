def uncompress_pl(pl):
    i = 0
    t = []
    while i < len(pl):
        first_byte = int.from_bytes(pl[i:i+1], byteorder="little")
        order = get_order(first_byte)
        #print(f" the order is {order}")
        i += 1
        for n in order:
            if i < len(pl):
                t.append(int.from_bytes(pl[i:i+n], byteorder="little"))
                i = i + n
    #print(t)
    return t

def compress_pl(pl , t1, t2):

    com_pl = b''
    left = len(pl) % 4
    try:
        for i in range(0, len(pl) - left, 4):
            t = (pl[i], pl[i+1], pl[i+2], pl[i+3])
            order = get_order_from_tuple(t)
           # print(f"order is {order} tuple is {t}")
            #print(order)
            if order[0] == 0 or order[1] == 0 or order[2] == 0 or order[3] == 0:
                print(f"error tuple is {t} in pl {pl}")
                print(f"pl1: {t1} pl2:{t2}")
            com_pl += order_to_byte(order)
            for j in range(0,4):
                com_pl += pl[i+j].to_bytes(order[j], byteorder="little")
        if left == 2:
            t = (pl[-2], pl[-1], 1,1)
            order = get_order_from_tuple(t)
            #print(order)
            com_pl += order_to_byte(order)
            com_pl += pl[-2].to_bytes(order[0], byteorder="little")
            com_pl += pl[-1].to_bytes(order[1], byteorder="little")
        elif left != 0:
            print("ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    except:
        print(f"--------------------error tuple is {t} in pl {pl}---------------------------")

        #print(f"pl1: {t1} pl2:{t2}")
        exit(-1)

    return com_pl

def order_to_byte(order):
    b = 0
    for n in order:
        #print(f"{b} << {n - 1}")
        b <<= 2
        b |= n - 1

    return b.to_bytes(1, byteorder="little")

def get_order_from_tuple(t):
    first = ((t[0].bit_length() + 7) // 8)
    second = ((t[1].bit_length() + 7) // 8)
    third = ((t[2].bit_length() + 7) // 8)
    fourth = ((t[3].bit_length() + 7) // 8)
    return first, second, third, fourth

def get_order(b):
    first = ((b & 192) >> 6) + 1
    second = ((b & 48) >> 4) + 1
    third = ((b & 12) >> 2) + 1
    fourth = (b & 3) + 1

    return first, second, third, fourth