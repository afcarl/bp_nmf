# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import time, functools
import librosa, bp_vbayes
from plot_utils import *

# <codecell>

specshow = functools.partial(imshow, aspect='auto', origin='lower', interpolation='nearest')

# <codecell>

x, sr = librosa.load('../data/PinkMoon.mp3')
n_fft = 512
hop_length = 512
Xc = librosa.stft(x, n_fft=n_fft, hop_length=hop_length)
X = abs(Xc)
K = 512
# reweight each frequency bin to conpensate for lower energy in high frequency
std_col = np.sqrt(np.var(X, axis=1, keepdims=True)) + 1e-8
X /= std_col
# make the smallest value of X no less than 80dB below the maximum value for numerical consideration
x_max = amax(X)
X[X < 1e-8 * x_max] = 1e-8 * x_max

# <codecell>

import scipy.stats
#reload(bp_vbayes)

def train(X, K, init_option, alpha, N, timed):
    bnmf = bp_vbayes.Bp_NMF(X, K=K, init_option=init_option, alpha=alpha)
    for n in xrange(N):
        start_t = time.time()
        bnmf.update(timed=timed[n])
        t = time.time() - start_t
        print 'Dictionary Learning: Iteration: {}, good K: {}, time: {:.2f}'.format(n, bnmf.good_k.shape[0], t)
    return bnmf

def encode(bnmf, X, K, ED, ED2, init_option, alpha, N, timed):
    bnmf = bp_vbayes.Bp_NMF(X, K=K, init_option=init_option, encoding=True, alpha=alpha)
    bnmf.ED, bnmf.ED2 = ED, ED2
    for n in xrange(N):
        start_t = time.time()
        bnmf.encode(timed=timed[n])
        t = time.time() - start_t
        print 'Encoding: Iteration: {}, good K: {}, time: {:.2f}'.format(n, bnmf.good_k.shape[0], t)
    return bnmf

# Take the middle 4000 frames for cross-validation
F = X.shape[0]
L = X.shape[1]
D = X[:, (L-4000)/2.:(L+4000)/2.]
# Model/training parameters
init_option = 'Rand'
alpha = 2.
N = 20
timed = ones((N,), dtype='bool')
timed[0] = False
#score = []
for i in xrange(1,5):
    idx = ones((4000,), dtype='bool')
    idx[i*800:(i+1)*800] = False
    D_test = D[:, ~idx]
    D_train = D[:, idx]
    bnmf = train(D_train, K, init_option, alpha, N, timed)
    Dict, Dict2 = bnmf.ED[:,bnmf.good_k].copy(), bnmf.ED2[:,bnmf.good_k].copy()
    bnmf = encode(bnmf, D_test[:F-192,:], Dict.shape[1], Dict[:F-192,:], Dict2[:F-192,:], init_option, alpha, N, timed)
    X_pred = dot(Dict[:,bnmf.good_k], (bnmf.ES * around(bnmf.EZ))[bnmf.good_k,:])
    sigma = sqrt( mean( (D_test[:F-192,:] - X_pred[:F-192,:])**2 ) )
    score.append(sum(scipy.stats.norm.logpdf(X_pred[:-192,:], loc=D_test[:-192,:], scale=sigma)))        

# <codecell>

score

# <codecell>

good_ks = [13]
