import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import math

plt.rc('font', family='Malgun Gothic')

# load csv
df = pd.read_csv('./sum/워라벨_sum.csv', parse_dates=[0], dtype=np.float64)

# normalized data { 'col1': [[0, 0], [0.2, 0.2], ...], 'col2': [[], [], ...], ... }
normalized_data = {}
# tensor for each columns { 'col1': [update_centroids, centroids, points, assignments], 'col2': [], ... }
col_tensors = {}

# initial centroids
raw_centroids = [[0, 0], [0.25, 0], [0.5, 0.125], [0.75, 0.5], [1, 1]]
#raw_centroids = [[0, 0], [0.1, 0.1], [0.2, 0.2], [0.3, 0.3], [0.4, 0.4], [0.5, 0.5], [0.6, 0.6], [0.7, 0.7], [0.8, 0.8], [0.9, 0.9]]

# for each columns (without date)
for coln in df.columns[1:]:
    col = df[coln]              # loaded column
    ncol = []                   # normalized column
    maxv = col[len(col) - 1]    # maximum value of columns (TODO: probably problematic)

    # normalize
    if maxv == 0:
        # if maximum value is 0, pretend it is 1 (preventing divide-by-zero)
        maxv = 1
    for i in range(len(col)):
        # add normalized col value into ncol
        #ncol.append([i / (len(col) - 1), col[i] / maxv])
        # make value smooth
        if i == 0:
            ncol.append([i / (len(col) - 1), (col[i] + col[i + 1]) / 2 / maxv])
        elif i == len(col) - 1:
            ncol.append([i / (len(col) - 1), (col[i - 1] + col[i]) / 2 / maxv])
        else:
            ncol.append([i / (len(col) - 1), (col[i - 1] + col[i] + col[i + 1]) / 3 / maxv])
    
    # add ncol to normalized columns
    normalized_data[coln] = ncol

    # create tensors
    points = tf.constant(ncol, dtype=np.float64)
    centroids = tf.Variable(raw_centroids, dtype=np.float64)

    points_expanded = tf.expand_dims(points, 0)
    centroids_expanded = tf.expand_dims(centroids, 1)

    distances = tf.reduce_sum(tf.square(tf.subtract(points_expanded, centroids_expanded)), 2)
    assignments = tf.argmin(distances, 0)
    
    means = []
    for c in range(len(raw_centroids)):
        means.append(tf.reduce_mean(
            tf.gather(points, 
                    tf.reshape(
                        tf.where(
                        tf.equal(assignments, c)
                        ),[1,-1])
                    ),reduction_indices=[1]))

    new_centroids = tf.concat(means, 0)
    update_centroids = tf.assign(centroids, new_centroids)

    # add columns' tensors to col_tensors
    col_tensors[coln] = [update_centroids, centroids, points, assignments]

with tf.Session() as sess:
    # init session
    sess.run(tf.global_variables_initializer())
    for coln, col_ten in col_tensors.items():   # run session per column
        for step in range(100): # number of iterations
            # run session
            [_, col_centroid_values, col_points_values, col_assignment_values] = sess.run(col_ten)
        
        # filtering code, useless for now
        '''
        state = {}
        for i in range(len(raw_centroids)):
            state[i] = []
        for i in range(len(col_points_values)):
            state[col_assignment_values[i]].append(col_points_values[i][0])
        
        state_invalid = False
        for k, v in state.items():
            if len(v) == 0:
                state_invalid = True
                break
        
        if state_invalid == True:
            print(coln)
            print('invalid state')
        else:
            print(coln)
            for k, v in state.items():
                print('cluster ' + str(k) + ': ' + str(math.floor(min(v) * len(col_points_values))) + ' ~ ' + str(math.floor(max(v) * len(col_points_values))))
                plt.scatter(col_points_values[:, 0], col_points_values[:, 1], c=col_assignment_values, s=50, alpha=0.5)
                plt.plot(col_centroid_values[:, 0], col_centroid_values[:, 1], 'kx', markersize=10)
        '''
        
        # plot result data
        plt.scatter(col_points_values[:, 0], col_points_values[:, 1], c=col_assignment_values, s=50, alpha=0.5)
        plt.plot(col_centroid_values[:, 0], col_centroid_values[:, 1], 'kx', markersize=10)

        # BEGIN show data per column (uncomment to use)
        #for i in raw_centroids:
        #    plt.plot(i[0], i[1], 'rx', markersize=10)
        #plt.title(coln)
        #plt.show()
        #plt.clf()
        # END show data per column

# BEGIN show total data (per column code must be commented out)
for i in raw_centroids:
    plt.plot(i[0], i[1], 'rx', markersize=10)
plt.show()
# END show total data