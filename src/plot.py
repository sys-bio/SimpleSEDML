from typing import Optional

class Plot:
    def __init__(self, x_var:str, y_var:str, z_var:Optional[str]=None, title:Optional[str]=None,
                 is_plot:bool=True)->None:  
        """
        Plot class to represent a plot in the script.
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
            var_clause = f"{self.x_var} vs {self.y_var}"
        else:
            var_clause = f"{self.x_var} vs {self.y_var} vs {self.z_var}"
        if self.title is None:
            return f"plot {var_clause}"
        else:
            return f"plot \"{self.title}\" {var_clause}"