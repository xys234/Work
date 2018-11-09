
import numpy as np
from services import report_service

logger = report_service.get_logger(__name__)


def bucket_rounding(mat):
    """
    bucket rounding and add the difference to the diagonal elements
    :param mat: an numpy 2d-array
    :return: an numpy 2d-array of dtype np.uint16
    """

    if len(mat.shape) != 2:
        logger.error("Input must be a 2-dimensional numpy array")
        raise ValueError("Input must be a 2-dimensional numpy array")

    rounded = np.zeros_like(mat, dtype=mat.dtype)
    for i in range(mat.shape[0]):
        residual = 0
        for j in range(mat.shape[1]):
            if mat[i, j] != 0:
                val = np.round(mat[i, j] + residual)
                residual += mat[i, j] - val
                rounded[i, j] = val

    total_diff = int(round(rounded.sum() - mat.sum()))
    diff = np.where(total_diff > 0, -1, 1)
    indices = np.argsort(np.diagonal(rounded))[::-1].astype(np.int16)[:np.abs(total_diff)]
    rounded[indices, indices] += diff
    return rounded.clip(min=0).astype(np.int16)


def normal_rounding(mat):
    """
    normal rounding and add the difference to the diagonal elements
    :param mat:
    :return:
    """
    if len(mat.shape) != 2:
        logger.error("Input must be a 2-dimensional numpy array")
        raise ValueError("Input must be a 2-dimensional numpy array")

    rounded = mat.round()
    total_diff = int(round(rounded.sum() - mat.sum()))
    diff = np.where(total_diff>0, -1, 1)
    indices = np.argsort(np.diagonal(rounded))[::-1].astype(np.int16)[:np.abs(total_diff)]
    rounded[indices, indices] += diff
    return rounded.clip(min=0).astype(np.int16)


if __name__ == '__main__':

    import time

    # test bucket rounding
    np.random.seed(42)
    m = np.random.random([5237, 5237])
    # m = np.random.random([1000,1000])
    # m = np.random.random([3,3])

    time_bucket, time_normal = 0.0, 0.0

    start = time.clock()
    m_bucket_rounded = bucket_rounding(m)
    end = time.clock()
    time_bucket = end - start

    start = time.clock()
    m_rounded = normal_rounding(m)
    end = time.clock()
    time_normal = end - start

    # print(m)
    # print(m_rounded)
    print("Input Total = {0:.2f}".format(m.sum()))
    print("Normal rounding Total = {0:.2f}".format(m_rounded.sum()))
    print("Bucket rounding Total = {0:.2f}".format(m_bucket_rounded.sum()))

    max_diff_row = np.argmax(np.abs(m.sum(axis=1) - m_rounded.sum(axis=1)))
    total_1, total_2 = m.sum(axis=1)[max_diff_row], m_rounded.sum(axis=1)[max_diff_row]
    print("Normal Rounding - Max row total difference: Before = {0:.2f} | After = {1:.2f}".format(total_1, total_2))

    max_diff_row = np.argmax(np.abs(m.sum(axis=0) - m_bucket_rounded.sum(axis=0)))
    total_1, total_2 = m.sum(axis=0)[max_diff_row], m_bucket_rounded.sum(axis=0)[max_diff_row]
    print("Bucket Rounding - Max column total difference: Before = {0:.2f} | After = {1:.2f}".format(total_1, total_2))

    print("Normal rounding Time = {0:.2f}".format(time_normal))
    print("Bucket rounding Time = {0:.2f}".format(time_bucket))