'''Manage variables in SED-ML documents.'''

"""
Display variables are used in plots and reports.
Parameters are used in parameter scans to specify values for the simulation.
Find default display variables.
Find display names for display variables.
Modify SEDML to use display names for display variables.
"""

import SimpleSEDML.constants as cn # type:ignore
from SimpleSEDML.model_information import ModelInformation # type:ignore
from SimpleSEDML.model import Model # type:ignore
import SimpleSEDML.utils as utils # type:ignore

import collections
from typing import Optional, List, Dict, Union
import warnings


ScopedVariableResult = collections.namedtuple("ScopedVariableResult",["dct", "lst"])


class VariableCollection(object):

    def __init__(self,
                model:Model,
                display_variables:Optional[List[str]]=None,
                scan_parameters:Optional[List[str]]=None) -> None:
        """
        Args:
            model (Model): _description_
            display_variables (Optional[List[str]], optional): _description_. Defaults to None.
            parameters (Optional[List[str]], optional): _description_. Defaults to None.
        """
        if scan_parameters is None:
            scan_parameters = []
        #
        self.model = model
        self._display_variables = display_variables
        self.scan_parameters:List[str] = scan_parameters
        #
        self.scope:Optional[str] = None

    @property
    def display_variables(self)->List[str]:
        """Returns list of display variables. If unspecified, use all variables
        from the first model.

        Returns:
            Optional[List[str]]: list of display variables
        """
        if self._display_variables is None:
            model_info = ModelInformation.getFromModel(self.model)
            display_variables = list(model_info.floating_species_dct.keys())
        else:
            display_variables = list(self._display_variables)
        if not cn.TIME in display_variables:
            display_variables.insert(0, cn.TIME)   # type: ignore
        return display_variables

    def addScanParameters(self, variable_names:List[str]) -> None:
        self.scan_parameters.extend(variable_names)

    def addDisplayVariables(self, variable_names:List[str]) -> None:
        self.display_variables.extend(variable_names)

    def getScopedVariables(self, 
            scope_str:Union[str, List[str]],
            is_time:bool=True, 
            is_parameters:bool=True,
            is_display_variables:bool=True) -> ScopedVariableResult:
        """Adds scope to the variables requested

        Args:
            scope_str (str or List[str]): string used to scope variables
            is_time (bool, optional): Include time
            is_parameters (bool, optional): Include parameters (from repeated task)
            is_display_variables (bool, optional): Include display variables

        Returns:
            ScopedVariableResult: Named tuple with two elements:
                dct (Dict[str, str]): Dictionary of scoped variables
                    key: variable name
                    value: scoped variable name
                list (List[str]): List of scoped variable names
        """
        ##
        def addScopeStr(variables:List[str])->Dict[str, str]:
            """Adds scope to the variables"""
            result_dct:dict = {}
            for scope_str in scope_strs:
                dct = {v: f"{scope_str}{cn.SCOPE_INDICATOR}{v}" for v in variables
                    if v != cn.TIME}
                for k in dct.keys():
                    if not k in result_dct:
                        result_dct[k] = []
                [result_dct[k].append(dct[k]) for k, v in dct.items()]
            if is_time and cn.TIME in variables:
                result_dct[cn.TIME] = [cn.TIME]
            return result_dct
        ##
        if isinstance(scope_str, str):
            scope_strs = [scope_str]
        else:
            scope_strs = scope_str
        #
        variables = []
        if is_parameters:
            variables.extend(self.scan_parameters)
        if is_display_variables:
            variables.extend(self.display_variables)
        if not is_time:
            if cn.TIME in variables:
                variables.remove(cn.TIME)
        result_dct = addScopeStr(variables)
        result_list:list = []
        [result_list.extend(v) for v in result_dct.values()]   # type:ignore
        return ScopedVariableResult(dct=result_dct, lst=result_list)
    
    def getDisplayNameDct(self, scope_str:Optional[str]=None) -> Dict[str, str]:
        """Finds the display names in a model.
        If an element does not have a display name, its element id is used.
        This dictionary is used in editing SEDML to use display names.

        Args:
            scope_str (str): string used to scope variables

        Returns:
            Dict[str, str]: Dictionary of display names
                key: scoped element_id
                value: display name
        """
        # Map element ids to display names
        dct = utils.makeDisplayNameDct(self.model.source)
        # Map variable names to scoped variable names
        if scope_str is None:
            scope_dct = {k: k for k in dct.keys()}  # No scoping
        else:
            scope_dct = self.getScopedVariables(scope_str, is_time=False, 
                    is_parameters=False, is_display_variables=True).dct
            # Use the first scoped variable name for each variable
            scope_dct = {k: v[0] for k, v in scope_dct.items() if k in dct}
        # Map scoped variable names to display names
        result_dct = {}
        for key, value in dct.items():
            if not key in self.display_variables:
                continue
            if (not isinstance(value, str)) and (len(value) > 1):
                warnings.warn(f"Multiple display names found for {key}: {value}. Using the first one.")
            result_dct[scope_dct[key]] = value[0] if isinstance(value, list) else value
        #
        return result_dct