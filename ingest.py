import json
import os

try:
    import kaggle
except ImportError:
    raise ImportError(
        "Kaggle API is not installed. "
        "Please install it using 'pip install kaggle'. "
        "Also, ensure you have your Kaggle API credentials set up correctly."
        "Refer to https://www.kaggle.com/docs/api for more details."
    )

try:
    from tqdm import tqdm
except ImportError:
    raise ImportError(
        "tqdm is not installed. "
        "Please install it using 'pip install tqdm'."
    )

def download_kaggle_dataset(dataset_name, path='data'):
    """
    Downloads a Kaggle dataset to the specified path.

    Parameters:
    - dataset_name: str, the name of the Kaggle dataset.


    """

    if not os.path.exists(path):
        os.makedirs(path)

    print(f"Downloading dataset '{dataset_name}' to '{path}'.")
    kaggle.api.dataset_download_files(dataset_name, path=path, unzip=True)
    print(f"Dataset '{dataset_name}' downloaded and extracted to '{path}'.")

    print("All datasets downloaded successfully.")
    print(f"Data is stored in {path}")


def load_dir(data_dir=None, n_files=None):
    """
    Loads data from the specified directory.

    Parameters:
    - data_dir: str, the directory containing the data files.

    Returns:
    - List of data files in the directory.
    """
    print(data_dir)
    if data_dir and not os.path.exists(data_dir):
        raise FileNotFoundError(f"The directory {data_dir} does not exist.")

    return {
        fname: load_json_file(os.path.join(data_dir, fname))
        for k, fname in tqdm(enumerate(os.listdir(data_dir)))
        if fname.endswith('.jsonl') and (n_files is None or k < n_files)
    }


def load_json_file(json_filename=None):
    """
    Loads data from the specified directory.

    Parameters:
    - data_dir: str, the directory containing the data files.

    Returns:
    - List of data files in the directory.
    """
    # TODO: Add error handling for file not found
    if json_filename and not os.path.exists(json_filename):
        raise FileNotFoundError(f"The file {json_filename} does not exist.")

    with open(json_filename) as json_in:
        return [json.loads(line) for line in json_in]


def load_all_data(data_dir=None, dir_lang_options=None, n_files=None):
    """
    Loads all data from the specified directory.

    Parameters:
    - data_dir: str, the directory containing the data files.
    - n_files: int, number of files to load (default is None, which loads all files).

    Returns:
    - A dictionary with filenames as keys and loaded JSON data as values.
    """
    if not data_dir or not os.path.exists(data_dir):
        raise FileNotFoundError(f"The directory {data_dir} does not exist.")

    if not dir_lang_options or not isinstance(dir_lang_options, list):
        raise ValueError(
            "dir_lang_options must be a list of language directories."
        )

    loaded_data = {}
    for lang_dir in dir_lang_options:
        if lang_dir not in loaded_data:
            loaded_data[lang_dir] = {}

        # Check if the directory exists and is a directory
        dirlang = os.path.join(data_dir, lang_dir)
        langdir_exists = os.path.exists(dirlang)
        langdir_isdir = os.path.isdir(dirlang)

        print(
            f"Checking directory: {dirlang} "
            f"(Exists: {langdir_exists}, IsDir: {langdir_isdir})"
        )

        # If the directory exists and is a directory, load the data
        if langdir_exists and langdir_isdir:
            print(f"Loading data from {dirlang}...")
            if lang_dir not in loaded_data:
                loaded_data[lang_dir] = {}
            if not len(loaded_data[lang_dir]):
                loaded_data[lang_dir] = load_dir(
                    data_dir=dirlang,
                    n_files=n_files
                )
        else:
            print(f"Directory {dirlang} does not exist or is not a directory.")

    print(
        f"Loaded data: {len(loaded_data)} languages "
        f"with {sum(len(v) for v in loaded_data.values())} files."
    )
    print(f"Data loaded successfully from {data_dir}.")

    # Return the loaded data
    return loaded_data


def identify_missing_keys(loaded_data):
    """
    Identifies missing keys in the loaded data.

    Parameters:
    - loaded_data: dict, the loaded data from the JSON files.

    Returns:
    - A set of missing keys (set), set of all keys (set)
    """

    set_of_keys = set()
    for _lang in loaded_data.keys():
        for filename in loaded_data[_lang].keys():
            for entry in loaded_data[_lang][filename]:
                set_of_keys.update(entry.keys())

    missing_keys = set()
    for _lang in loaded_data.keys():
        for filename in loaded_data[_lang].keys():
            for entry in loaded_data[_lang][filename]:
                missing_keys.update(
                    [key for key in set_of_keys if key not in entry.keys()]
                )

    print(f"Set of keys: {set_of_keys}")
    print(f"Missing keys: {missing_keys}")

    return set_of_keys, missing_keys


if __name__ == "__main__":

    lang_options = ['en', 'fr']
    dir_lang_options = [f"{lang}wiki_namespace_0" for lang in lang_options]
    dataset = "wikimedia-foundation/wikipedia-structured-contents"
    data_dir = "data"

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Output directory created at {data_dir}.")

    data_exists = [os.path.exists(_data_dir) for _data_dir in dir_lang_options]
    data_exists = True in data_exists

    if not data_exists:
        print("Data already exists, skipping download.")
    elif input('Should we start the download [y/n]: ').strip().lower() == 'y':
        download_kaggle_dataset(dataset_name=dataset, path=data_dir)

    # Load the data
    n_files = 1  # Number of files to load, set to None to load all
    loaded_data = load_all_data(
        data_dir=data_dir,
        dir_lang_options=dir_lang_options,
        n_files=n_files
    )

    # Identify keys and partially missing keys
    set_of_keys, missing_keys = identify_missing_keys(loaded_data)
