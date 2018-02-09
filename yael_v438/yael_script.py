import numpy as np
import scipy.linalg
from yael import ynumpy
import json, codecs
import time

def process():
    # make a big matrix with all image descriptors
    image_descs = np.random.rand(1000,512)

    image_descs = np.array(image_descs).astype('float32')
    all_desc = np.vstack(image_descs)

    k = 64
    #n_sample = k * 1000
    n_sample = 1000

    # choose n_sample descriptors at random
    sample_indices = np.random.choice(all_desc.shape[0], n_sample)
    sample = all_desc[sample_indices]

    # until now sample was in uint8. Convert to float32
    #sample = sample.astype('float32')

    # compute mean and covariance matrix for the PCA
    mean = sample.mean(axis=0)
    sample = sample - mean
    cov = np.dot(sample.T, sample)

    # compute PCA matrix and keep only 64 dimensions
    eigvals, eigvecs = scipy.linalg.eig(cov)
    perm = eigvals.argsort()  # sort by increasing eigenvalue
    pca_transform = eigvecs[:, perm[512-64-1: 512-1]]  # eigenvectors for the 64 last eigenvalues


    # transform sample with PCA (note that numpy imposes line-vectors,
    # so we right-multiply the vectors)
    sample = np.dot(sample, pca_transform)

    # train GMM
    gmm = ynumpy.gmm_learn(sample, k)

    image_fvs = []
    for image_desc in image_descs:
        # apply the PCA to the image descriptor
        image_desc = np.dot(image_desc - mean, pca_transform)
        # compute the Fisher vector, using only the derivative w.r.t mu
        image_desc = np.expand_dims(image_desc, axis=0)
        fv = ynumpy.fisher(gmm, image_desc, include='mu')
        image_fvs.append(fv)

    # make one matrix with all FVs


    # compute mean and covariance matrix for the PCA
    image_fvs = np.vstack(image_fvs)
    pca_transform2 = PCA(image_fvs)
    image_fvs = np.dot(image_fvs, pca_transform2)

    # normalizations are done on all descriptors at once

    # power-normalization
    image_fvs = np.sign(image_fvs) * np.abs(image_fvs) ** 0.5


    # L2 normalize
    norms = np.sqrt(np.sum(image_fvs ** 2, 1))
    image_fvs /= norms.reshape(-1, 1)

    print(image_fvs)
    path = "yael_result" + ".json"
    json.dump(np.real(image_fvs).tolist(), codecs.open(path, 'w', encoding='utf-8'), separators=(',', ':'),
              sort_keys=True)



    return


def isWorking():
    return "YAY! I'M IN YAEL SCRIPT!"

def PCA(matrix):
    print("PCA")
    t1 = time.time()
    #sample = np.random.rand(1,2048)
    sample = matrix
    print(time.time() - t1)
    print("Random matrix obtained")
    mean = sample.mean(axis=0)
    sample = sample - mean
    print(time.time() - t1)
    print("Mean Calculated")
    cov = np.dot(sample.T, sample)
    print(time.time() - t1)
    print("Dot Calculated")
    eigvals, eigvecs = scipy.linalg.eig(cov)
    print(time.time() - t1)
    print("calculated eigvals & eigvecs")
    perm = eigvals.argsort()  # sort by increasing eigenvalue
    pca_transform = eigvecs[:, perm[matrix.shape[1]-1-512:matrix.shape[1]-1]]  # eigenvectors for the 64 last eigenvalues
    return pca_transform


process()