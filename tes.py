import numpy as np

feature_weights_0 = np.array([0.00059435, 0.01919768, 0.05873248, -0.02695521736796405])
feature_weights_1 = np.array([-0.00303212, 0.02074924, 0.07094721, -0.05955500979744721])
feature_weights_2 = np.array([-0.00607127, 0.02527233, 0.0790592, -0.11719479853351966])
feature_weights_3 = np.array([-0.00630675, 0.02912954, 0.0811169, -0.1601507238663965])
feature_weights_4 = np.array([-0.0027939, 0.02795119, 0.07740094, -0.12095795716822455])
feature_weights_5 = np.array([0.00404156, 0.02623495, 0.07188201, -0.020223479611829576])

feature_weights_list = [feature_weights_0, feature_weights_1, feature_weights_2, feature_weights_3, feature_weights_4, feature_weights_5]

np.save('feature_weights.npy', feature_weights_list)