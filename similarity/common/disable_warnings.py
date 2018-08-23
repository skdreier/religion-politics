import warnings

# we need numpy 1.5, but spacy/h5py run against an earlier version;
# these warnings are benign and very annoying
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
