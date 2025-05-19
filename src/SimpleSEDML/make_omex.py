'''Creates a Combine archive and writes it to an OMEX file.'''

# Author: Lician P. Smith, May 19, 2025

from biosimulators_utils.combine.io import CombineArchiveWriter  # type: ignore
from biomodels_qc.utils import build_combine_archive  # type: ignore
import os
from typing import Optional

combine_writer = CombineArchiveWriter()


def makeOMEX(project_id:str,
                omex_dir:Optional[str]=None,
                project_path:Optional[str]=None,
                is_write_omex:bool=True,
                sbml_master = None):
    """
    Process a project directory to create a Combine archive and write it to an OMEX file.
    Args:
        project_id (str): The ID of the project.
        omex_dir (str): The directory where the OMEX file will be written.
        project_path (str): The path to the project directory.
        is_write_omex (bool): Whether to write the OMEX file or not.
        sbml_master (str): The path to the SBML master file.
    """
    # Initializations
    if project_path is None:
        project_path = os.path.join(os.path.dirname(__file__))
    if omex_dir is None:
        omex_dir = os.path.join(os.path.dirname(__file__), 'omex')
    manifest_filename = os.path.join(project_path, 'manifest.xml')
    master_files = []
    if sbml_master:
        master_files.append(sbml_master)
    if os.path.exists(manifest_filename):
        #Have to do this, otherwise build_combine_archive creates a new one!
        os.remove(manifest_filename)
    archive = build_combine_archive(project_path, master_files)
    if is_write_omex:
        combine_writer.run(archive, project_path, omex_dir + "/" + project_id + ".omex")
    #Write the new manifest.xml file:
    combine_writer.write_manifest(archive.contents, manifest_filename)