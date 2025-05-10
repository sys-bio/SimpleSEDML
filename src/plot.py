from typing import Optional, List, Union

class Plot:
    def __init__(self, x_var:str, y_var:Union[str, List[str]], z_var:Optional[str]=None, title:Optional[str]=None,
                 is_plot:bool=True)->None:  
        """
        Plot class to represent a plot in the script. The following cases are supported:
           plot x vs y (z is None, y is str)
           plot x vs y1, y2, y3 (z is None, y is a list of str)
           plot x vs y vs z  (z is a str, y is str)

        Args:
            x_var (str): x variable
            y_var (str): y variable
            z_var (str, optional): z variable. Defaults to None.
            title (str, optional): title of the plot. Defaults to None.
        """
        self.x_var = x_var
        self.y_var = y_var
        self.z_var = z_var
        self.title = title
        self.is_plot = is_plot

    def __str__(self)->str:
        if not self.is_plot:
            return ""
        if self.z_var is None:
            if isinstance(self.y_var, str):
                y_vars = [self.y_var]
            else:
                y_vars = self.y_var
            var_clause = f'{self.x_var} vs {", ".join(y_vars)}'
        else:
            if not isinstance(self.y_var, str):
                raise ValueError("y_var must be a string when z_var is provided")
            var_clause = f"{self.x_var} vs {self.y_var} vs {self.z_var}"
        if self.title is None:
            return f"plot {var_clause}"
        else:
            return f"plot \"{self.title}\" {var_clause}"
        
    def changeVariableScope(self, old_scope:str, new_scope:str)->None:
        """Change the scope of the variables in the plot. For example,
        change "model1.x" to "task1.x"

        Args:
            old_scope (str): old scope
            new_scope (str): new scope
        """
        if self.x_var.startswith(old_scope):
            self.x_var = self.x_var.replace(old_scope, new_scope)
        if isinstance(self.y_var, str) and self.y_var.startswith(old_scope):
            self.y_var = self.y_var.replace(old_scope, new_scope)
        elif isinstance(self.y_var, list):
            for i in range(len(self.y_var)):
                if self.y_var[i].startswith(old_scope):
                    self.y_var[i] = self.y_var[i].replace(old_scope, new_scope)
        if self.z_var is not None and self.z_var.startswith(old_scope):
            self.z_var = self.z_var.replace(old_scope, new_scope)