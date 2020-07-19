def NonCrossingPaths(distance_matrix, path, max_iterations=100):
    path = path[:]
    for iter in range(max_iterations):
        swap = False
        for i2 in range(1, len(path) - 2):
            i1 = i2 - 1
            for i4 in range(i2 + 2, len(path)):
                i3 = i4 - 1
                if distance_matrix[path[i1]][path[i2]] + distance_matrix[path[i3]][path[i4]] > distance_matrix[path[i1]][path[i3]] + distance_matrix[path[i2]][path[i4]]:
                    path[i2], path[i3] = path[i3], path[i2]
                    swap = True
        if not swap:
            break
        print(iter)
    return path
