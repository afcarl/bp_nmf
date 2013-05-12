# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, time, functools
import scipy.io as sio
import scipy.stats
import librosa, bp_vbayes
import utils

# <codecell>

## Data pre-processing parameters
reload(utils)
ID = 'FunkyKingston'
filename = '../data/{}.mp3'.format(ID)
n_fft = 512
hop_length = 512
reweight = False
X, std_col = utils.get_data(filename, n_fft, hop_length, reweight=reweight, sr=22050)
# Take the middle 4000 frames for cross-validation
F, L = X.shape
D = X[:, (L-4000)/2.:(L+4000)/2.]

## Model training parameters
K = 512
init_option = 'Rand'
alpha = 2.
N = 20

# <codecell>

def logexppdf(x, mu):
    return (-np.log(mu) - x / mu)

def cv_band_expansion(is_timed, ratio):
    timed = utils.gen_train_seq(is_timed, N)
    score1 = []
    score2 = []
    score3 = []
    good_ks = []
    for i in xrange(5):
        idx = ones((4000,), dtype='bool')
        idx[i*800:(i+1)*800] = False
        D_test = D[:, ~idx]
        D_train = D[:, idx]
        bnmf = utils.train(D_train, K, init_option, alpha, N, timed)
        Dict, Dict2 = bnmf.ED[:,bnmf.good_k].copy(), bnmf.ED2[:,bnmf.good_k].copy()
        bnmf = utils.encode(bnmf, D_test[:F-192*ratio,:], Dict.shape[1], Dict[:F-192*ratio,:], Dict2[:F-192*ratio,:], init_option, alpha, N, timed)
        X_pred = dot(Dict[:,bnmf.good_k], (bnmf.ES * around(bnmf.EZ))[bnmf.good_k,:])
        sigma = sqrt( mean( (D_test[:F-192*ratio,:] - X_pred[:F-192*ratio,:])**2 ) )
        score1.append(np.exp(np.mean(scipy.stats.norm.logpdf(X_pred[:-192*ratio,:], loc=D_test[:-192*ratio,:], scale=sigma))))  
        score2.append(np.exp(np.mean(logexppdf(D_test[:-192*ratio,:], X_pred[:-192*ratio,:]))))
        score3.append(np.exp(np.mean(logexppdf(X_pred[:-192*ratio,:], D_test[:-192*ratio,:]))))
        good_ks.append(bnmf.good_k.shape[0])
    print good_ks
    print score1
    print score2
    print score3
    name = utils.gen_save_name(ID, is_timed, reweight, n_fft, hop_length, K)
    sio.savemat('{}.mat'.format(name), {'goodks':good_ks, 'score1':score1, 'score2':score2, 'score3':score3})    

# <headingcell level=1>

# Band expansion experiemnt for time-dependent BP-NMF

# <codecell>

'''
Band expansion for time-dependent BP-NMF
'''
cv_band_expansion(True)

# <headingcell level=1>

# Band expansion experiment for i.i.d. BP-NMF

# <codecell>

'''
Band expansion for i.i.d. BP-NMF
'''
cv_band_expansion(False, 1)

# <codecell>

score = [-49945.257034776252, -39861.275459696284, -100529.18378716003, -39013.04957121201, -129388.06924422563]
mean(score)

# <codecell>

score = [-88306.731511612772, -74544.406821825396, -50010.272902419456, -64277.956297935161, -65453.456169710837]
mean(score)

# <codecell>

d = sio.loadmat('bnmf_PinkMoon_Nscale_20N_F512_H512_K512.mat')
score = d['score2']
print mean(score), sqrt(var(score))

# <codecell>

print mean(d['goodks']), sqrt(var(d['goodks']))

# <codecell>

