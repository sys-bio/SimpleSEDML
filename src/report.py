class Report:
    def __init__(self, title):
        self.title = title
        self.reports = []

    def addData(self, *args):
        """
        List of data to report

        Args:
            *args: list of data to report
        """
        self.data.append(*args)

    def __str__(self)->str:
        return "\n".join([f'report "{self.title}" {plot}' for plot in self.reports])