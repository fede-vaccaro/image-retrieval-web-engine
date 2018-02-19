import sys
import numpy as np
import numpy.linalg as LA
import scipy.linalg
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
from sklearn.externals import joblib
from yael import ynumpy
from yael import yael
import time, h5py

def process(signature=None):
    # make a big matrix with all image descriptors

    all_desc = []
    #handle the case it's requested to process the entire dataset
    if signature is None:
        h5f = h5py.File("feature_matrix.h5", 'r')
        feats = h5f['feature_matrix'][:]
        h5f.close()

        #normalize input matrix to avoid GMM crash
        feats = normalize(feats, axis=1, norm='l2')

        #ensure thet the descriptors are FP32 and put them in a matrix
        image_descs = np.array(feats).astype('float32')
        all_desc = np.vstack(image_descs)

    try:
        #if available, load GMM model and PCA
        h5f = h5py.File("GMM.h5", 'r')
        gmm = np.array(h5f['gmm1']).astype('float32'), np.array(h5f['gmm2']).astype('float32'), np.array(h5f['gmm3']).astype('float32')
        pca_transform = joblib.load('pca_transform_gmm.pkl')
        h5f.close()
        print("there are GMM and pca_transform")
    except:
        #handle the case where there aren't the needed data to process.
        if signature is not None:
            error = "No needed data found. Abort."
            print(error)
            return error

        #in case it's needed to populate the DB
        print("there aren't GMM and pca_transform: computing.")
        #k is the GMM dimension
        k = 512
        n_sample = k * 100

        #choose n_sample descriptors at random
        sample_indices = np.random.choice(all_desc.shape[0], n_sample)
        sample = all_desc[sample_indices]

        #compute PCA and transform the samples
        pca_transform = myPCA(sample, k)
        sample = pca_transform.transform(sample)

        #train GMM
        print("Start fitting GMM")
        GMM_ = GaussianMixture(n_components=k, covariance_type='diag', verbose_interval=1)
        t1 = time.time()
        GMM_.fit(sample)
        print("GMM fit in %s") %(time.time() - t1)

        #Get GMM matrices
        w_, mu_, sigma_ = GMM_.weights_, GMM_.means_, GMM_.covariances_

        #Convert to FP32 (from FP64)
        gmm = w_.astype('float32'), mu_.astype('float32'), sigma_.astype('float32')

        #Save GMM
        h5f = h5py.File("GMM.h5", 'w')
        h5f.create_dataset('gmm1', data=gmm[0])
        h5f.create_dataset('gmm2', data=gmm[1])
        h5f.create_dataset('gmm3', data=gmm[2])
        h5f.close()

        #Save PCA model
        joblib.dump(pca_transform, 'pca_transform_gmm.pkl')

    #compute FVS

    image_fvs = []
    if signature is not None:
        image_descs = np.array(signature)
        image_descs = image_descs.reshape(1,-1)
        image_descs = image_descs.astype('float32')

    for image_desc in image_descs:
        # apply the PCA to the image descriptor
        image_desc = np.expand_dims(image_desc, axis=0)
        image_desc = pca_transform.transform(image_desc - image_desc.mean())
        # compute the Fisher vector, using only the derivative w.r.t mu
        fv = ynumpy.fisher(gmm, image_desc, include='mu')
        image_fvs.append(fv)

    print("FVS processed.")

    # make one matrix with all FVs
    image_fvs = np.vstack(image_fvs)

    #compute PCA to reduce FVs dimensionality (which is k^2)
    if signature is None:
        pca_transform2 = myPCA(image_fvs, dim=512)
        image_fvs = pca_transform2.transform(image_fvs)

        #Save FVS PCA
        joblib.dump(pca_transform2, 'pca_transform_fvs.pkl')

        #Save processed vectors that must be insert in the DB
        h5f = h5py.File("image_fvs.h5", 'w')
        h5f.create_dataset('image_fvs', data=np.real(image_fvs))
        h5f.close()


        print("YAEL SCRIPT: Mission accomplished!")
        return "YAEL SCRIPT: Mission accomplished!"

    pca_transform2 = joblib.load('pca_transform_fvs.pkl')
    image_fv = pca_transform2.transform(image_fvs)
    return image_fv.tolist()

def myPCA(matrix, dim):
    print("Start calculating PCA of dim %s starting by %s") %(dim, matrix.shape)
    t1 = time.time()
    pca = PCA(n_components=dim)
    pca.fit(matrix)
    print("PCA calculated in %s") %(time.time() - t1)
    return pca

#if want to run it from shell
#desc = np.random.rand(512)
process()