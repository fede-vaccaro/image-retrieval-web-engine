import sys
import numpy as np
import numpy.linalg as LA
import scipy.linalg
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
from sklearn.externals import joblib
from multiprocessing.dummy import Pool as ThreadPool
from yael import ynumpy
import time, h5py

def calculateFV(img):
    im_matrix_ = np.array(img)
    # k is the GMM dimension
    k = 256
    n_sample = im_matrix_.shape[0]

    # compute PCA and transform the samples
    pca_transform = myPCA(im_matrix_, k)
    im_matrix_ = pca_transform.transform(im_matrix_)

    # train GMM
    print("Start fitting GMM")
    GMM_ = GaussianMixture(n_components=k, covariance_type='diag', verbose_interval=1)
    t1 = time.time()
    GMM_.fit(im_matrix_)
    print("GMM fit in {}".format(time.time() - t1))

    # Get GMM matrices
    w_, mu_, sigma_ = GMM_.weights_, GMM_.means_, GMM_.covariances_

    # Convert to FP32 (from FP64)
    gmm = w_.astype('float32'), mu_.astype('float32'), sigma_.astype('float32')

    # compute FVS
    print("Processing FV of image i")
    # compute the Fisher vector, using only the derivative w.r.t mu
    fv = ynumpy.fisher(gmm, im_matrix_, include='mu')
    print("FV processed.")
    return fv


# function to be mapped over
def calculateParallel(tensor, threads=16):
    pool = ThreadPool(threads)
    results = pool.map(calculateFV, tensor)
    pool.close()
    pool.join()
    return np.array(results)

def process():
    # make a big matrix with all image descriptors

    t = time.time()

    n_images = 256
    n_windows = 500

    all_desc = []

    h5f = h5py.File("feature_matrix_with_windows.h5", 'r')
    for i in range(n_images):
        feats = normalize(h5f['feature_matrix_image_{}'.format(i)][:], axis=1, norm='l2')
        all_desc.append(feats)
        print(feats.shape)
    h5f.close()

    # ensure that the descriptors are FP32 and put them in a matrix
    image_descs = np.array(all_desc)


    print(image_descs.shape)

    image_fvs = calculateParallel(image_descs, threads=16)


    # make one matrix with all FVs
    image_fvs = np.vstack(image_fvs)
    pca_transform_fvs = myPCA(image_fvs, 256)
    image_fvs_ = pca_transform_fvs.transform(image_fvs)
    print("FVS shape is: {}".format(image_fvs_.shape))

    # power-normalization
    image_fvs_ = np.sign(image_fvs_) * np.abs(image_fvs_) ** 0.5

    # L2 normalize
    image_fvs_ = normalize(image_fvs_, norm='l2', axis=1)

    print("Computation executed in: {}s".format(time.time() - t))

    # Save FVS PCA
    joblib.dump(pca_transform_fvs, 'pca_transform_fvs.pkl')


    # Save processed vectors that must be insert in the DB
    h5f = h5py.File("image_fvs.h5", 'w')
    h5f.create_dataset('image_fvs', data=np.real(image_fvs_))
    h5f.close()

    print("YAEL SCRIPT: Mission accomplished!")
    return "YAEL SCRIPT: Mission accomplished!"


def myPCA(matrix, dim):
    print("Start calculating PCA of dim %s starting by %s") % (dim, matrix.shape)
    t1 = time.time()
    pca = PCA(n_components=dim)
    pca.fit(matrix)
    print("PCA calculated in %s") % (time.time() - t1)
    return pca


process()
