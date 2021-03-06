
import h5py
import os

from pylearn2.datasets import preprocessing

import hdf5_data_preprocessors
import paths
import choose


def preprocess_grasp_dataset(attribs):

    pipeline = preprocessing.Pipeline()

    pipeline.items.append(hdf5_data_preprocessors.CopyInRaw(
        source_dataset_filepath=attribs["raw_filepath"],
        input_keys=('rgbd_patches', 'rgbd_patch_labels'),
        output_keys=('patches', 'patch_labels')
    ))

    pipeline.items.append(hdf5_data_preprocessors.RandomizePatches(
        keys=('patches', 'patch_labels')
    ))

    pipeline.items.append(hdf5_data_preprocessors.LecunSubtractiveDivisiveLCN(
        in_key='patches',
        out_key='normalized_patches'
    ))

    #now we split the patches up into train, test, and valid sets
    pipeline.items.append(hdf5_data_preprocessors.SplitGraspPatches(
        output_keys=(
            ("train_patches", "train_patch_labels"),
            ("valid_patches", "valid_patch_labels"),
            ("test_patches", "test_patch_labels")
        ),
        output_weights=(.8, .1, .1),
        source_keys=("normalized_patches", "patch_labels")))

    #now we swap around the axis so the data fits nicely onto the gpu
    # C01B rather than B01C
    pipeline.items.append(hdf5_data_preprocessors.MakeC01B())

    #now lets actually make a new dataset and run it through the pipeline
    if not os.path.exists(paths.PROCESSED_TRAINING_DATASET_DIR):
        os.makedirs(paths.PROCESSED_TRAINING_DATASET_DIR)

    hd5f_dataset = h5py.File(attribs["output_filepath"])
    pipeline.apply(hd5f_dataset)


if __name__ == "__main__":

    raw_data_filename = choose.choose_from(paths.RAW_TRAINING_DATASET_DIR)
    raw_data_filepath = paths.RAW_TRAINING_DATASET_DIR + raw_data_filename

    preprocess_attribs = dict(sets=("train", "test", "valid"),
                              raw_filepath=raw_data_filepath,
                              output_filepath=paths.PROCESSED_TRAINING_DATASET_DIR + 'processed_' + raw_data_filename)

    preprocess_grasp_dataset(preprocess_attribs)
