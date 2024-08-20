import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Union
from pandas.core.api import DataFrame
from pandas.core.series import Series

LABEL = "label"
PROBABILITY = "probability"
CUT_CODE = "cut_code"
LIFT = "lift"
CHART_DEFAULT_TITLE = "Cumulative Lift"
CHART_DEFAULT_X_LABEL = "Decile"
CHART_DEFAULT_Y_LABEL = "Lift"
YELLOW_COLOR = "y"
GREEN_COLOR = "g"
CIRCLE_MARKER = "o"
DASHED_LINE = "--"
TOP = "top"
BOTTOM = "bottom"
RIGHT = "right"
LEFT = "left"
BOLD = "bold"


class Lift(object):
    """Provides the ability to measure Model Lift performance.

    :param Union[List[float], Series] probabilities: a list of probability
    :param Union[List[Union[int, float]], Series] labels: a list of label
    :param Optional[int] cut_count: qut cut count

    Example.
    ----------
    >>> ## Using a list of probabilities and a list of labels
    >>> from support.model.evaluation.lift import Lift
    >>> probabilities = [0.98844259, 0.97958927, 0.96879274, 0.91803913, 0.90388280, 0.89740218, 0.89218740, 0.85228005, 0.85062156, 0.83946331, 0.79613996, 0.79147099, 0.78313609, 0.78011108, 0.75917612, 0.75048448, 0.74827577, 0.74352021, 0.73319971, 0.72428445, 0.72091845, 0.71829122, 0.69528244, 0.69390392, 0.68533424, 0.66817384, 0.64531833, 0.62498809, 0.60522340, 0.59490865, 0.58700569, 0.57259372, 0.54032699, 0.50566215, 0.50236339, 0.45088087, 0.42459046, 0.38095339, 0.32216346, 0.30489529, 0.29647220, 0.26267951, 0.25731572, 0.24795000, 0.21752568, 0.16134969, 0.13622810, 0.12323340, 0.08032223, 0.03863539, ]
    >>> labels = [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]
    >>> lift = Lift(probabilities=probabilities, labels=labels)
    >>> lift.get_cum_lift()
    +----------+----------+
    |          |     lift |
    | cut_code |          |
    +==========+==========+
    |        0 | 2.500000 |
    +----------+----------+
    |        1 | 2.000000 |
    +----------+----------+
    |        2 | 1.666667 |
    +----------+----------+
    |        3 | 1.500000 |
    +----------+----------+
    |        4 | 1.400000 |
    +----------+----------+
    |        5 | 1.333333 |
    +----------+----------+
    |        6 | 1.214286 |
    +----------+----------+
    |        7 | 1.125000 |
    +----------+----------+
    |        8 | 1.055556 |
    +----------+----------+
    |        9 | 1.000000 |
    +----------+----------+

    >>> ## Using pandas dataframe
    >>> pd_df = pd.DataFrame({'proba': self.probabilities, 'labels': self.labels})
    >>> lift = Lift(probabilities=pd_df['proba'], labels=pd_df['labels'])
    >>> lift.get_cum_lift()
    +----------+----------+
    |          |     lift |
    | cut_code |          |
    +==========+==========+
    |        0 | 2.500000 |
    +----------+----------+
    |        1 | 2.000000 |
    +----------+----------+
    |        2 | 1.666667 |
    +----------+----------+
    |        3 | 1.500000 |
    +----------+----------+
    |        4 | 1.400000 |
    +----------+----------+
    |        5 | 1.333333 |
    +----------+----------+
    |        6 | 1.214286 |
    +----------+----------+
    |        7 | 1.125000 |
    +----------+----------+
    |        8 | 1.055556 |
    +----------+----------+
    |        9 | 1.000000 |
    +----------+----------+

    >>> ## cut_count = 5
    >>> lift = Lift(probabilities=probabilities, labels=labels, cut_count=5)
    >>> lift.get_cum_lift()
                  lift
    cut_code
    0         2.000000
    1         1.500000
    2         1.333333
    3         1.125000
    4         1.000000
    """

    def __init__(self,
                 probabilities: Union[List[float], Series],
                 labels: Union[List[Union[int, float]], Series],
                 cut_count: Optional[int] = 10):
        self._probabilities = tuple(probabilities)
        self._labels = tuple(labels)
        self._cut_count = cut_count

    def _cumulative_lift(self) -> DataFrame:
        """Get cumulative lift.

        :returns: cumulative lift
        :retype: DataFrame
        """
        self._check_validation()
        pred_df = pd.DataFrame({LABEL: self._labels, PROBABILITY: self._probabilities})
        pred_df[CUT_CODE] = pd.qcut(pred_df.probability, self._cut_count, labels=np.arange(self._cut_count - 1, -1, -1),
                                    duplicates='drop')
        mean_label_count = np.mean(pred_df[LABEL])
        cut_df = pred_df.groupby(CUT_CODE)[LABEL].agg(['sum', 'count'])
        cut_df = cut_df.sort_index(ascending=False)
        cut_df[LIFT] = (cut_df['sum'].cumsum() / cut_df['count'].cumsum()) / mean_label_count
        return cut_df[[LIFT]]

    def get_cum_lift(self) -> DataFrame:
        """Get cumulative lift.

        :returns: cumulative lift
        :retype: DataFrame

        >>> cum_lift = lift.get_cum_lift()
                      lift
        cut_code
        0         2.500000
        1         2.000000
        2         1.666667
        3         1.500000
        4         1.400000
        5         1.333333
        6         1.214286
        7         1.125000
        8         1.055556
        9         1.000000
        """
        return self._cumulative_lift()

    def get_cum_lift_of_dict(self) -> Dict:
        """Get cumulative lift of dictionary type.

        :returns: a dictionary of cumulative lift
        :retype: Dict

        >>> cum_lift_to_dict = lift.get_cum_lift_of_dict()
        {
            0: 2.5,
            1: 2.0,
            2: 1.6666666666666665,
            3: 1.4999999999999998,
            4: 1.4000000000000001,
            5: 1.XXXXX333,
            6: 1.2XXXXX7142,
            7: 1.125,
            8: 1.0555555555555556,
            9: 1.0
        }
        """
        cum_lift = self.get_cum_lift().to_dict(orient='split')
        indexes = cum_lift["index"]
        data = cum_lift["data"]
        cum_lift_of_dict = {}
        for index in indexes:
            cum_lift_of_dict[index] = data[index][0]
        return cum_lift_of_dict

    def get_cum_lift_of_list(self) -> List:
        """Get cumulative lift of list type.

        :returns: a list of cumulative lift
        :retype: List

        >>> cum_lift_to_dict = lift.get_cum_lift_of_list()
        [2.5,
         2.0,
         1.6666666666666665,
         1.4999999999999998,
         1.4000000000000001,
         1.XXXXX333,
         1.2XXXXX7142,
         1.125,
         1.0555555555555556,
         1.0]
        """
        return list(self._cumulative_lift()["lift"])

    def get_first_cum_lift(self) -> float:
        """Get first cumulative lift.

        :returns: a float of first cumulative lift
        :retype: float

        >>> first_cum_lift = lift.get_first_cum_lift()
        2.5
        """
        return self.get_cum_lift_of_dict()[0]

    def get_cum_lift_summary(self) -> Dict:
        """Get cumulative lift summaries.

        :returns: a nested dictionary of cumulative lift summaries.
        :retype: Dict

        >>> cum_lift_summary = lift.get_cum_lift_summary()
        {
            "lift": {
                "cum_lift_10": 2.5,
                "cum_lift": {
                    0: 2.5,
                    1: 2.0,
                    2: 1.6666666666666665,
                    3: 1.4999999999999998,
                    4: 1.4000000000000001,
                    5: 1.XXXXX333,
                    6: 1.2XXXXX7142,
                    7: 1.125,
                    8: 1.0555555555555556,
                    9: 1.0
                }
            }
        }
        """
        return {
            "lift": {
                f"cum_lift_{str(self._cut_count)}": self.get_first_cum_lift(),
                "cum_lift": self.get_cum_lift_of_dict()
            }
        }

    def plot(self,
             line_width: Optional[int] = 3,
             title: Optional[str] = CHART_DEFAULT_TITLE,
             x_label: Optional[str] = CHART_DEFAULT_X_LABEL,
             y_label: Optional[str] = CHART_DEFAULT_Y_LABEL,
             compare_lift: Optional[List] = ()) -> None:
        """Plot cumulative lift. Run "%matplotlib inline" if you don't see the plot.

        :param Optional[int] line_width: line width. (default = 3)
        :param Optional[str] title: chart title.
        :param Optional[str] x_label: label x axis.
        :param Optional[str] y_label: label y axis.
        :param Optional[List] compare_lift: vs cumulative lift of list type. e.g. [2.48, 1.92, 1.60, 1.50, 1.40, 1.28, 1.19, 1.10, 1.04, 1.0]

        >>> lift.plot()

        .. image:: /images/cumulative_lift.png

        >>> # Lift 비교 시 compare_lift를 입력하여 plot을 출력
        >>> _compare_lift = [2.48, 1.92, 1.60, 1.50, 1.40, 1.28, 1.19, 1.10, 1.04, 1.0]
        >>> lift.plot(compare_lift=_compare_lift)

        .. image:: /images/cumulative_lift_comparison.png

        >>> # line_width, title, x_label, y_label Optional하게 변경 가능
        >>> lift.plot(line_width=5, title='lift', x_label='decile', y_label='lift')

        .. image:: /images/cumulative_lift_title_change.png
        """
        import matplotlib.pyplot as plot
        from decimal import Decimal

        cum_lift_of_dict = self.get_cum_lift_of_dict()
        decile = [key for key in cum_lift_of_dict.keys()]
        current_lift = [value for value in cum_lift_of_dict.values()]

        with plot.style.context('default'): #dark_background
            # rcParams
            plot.rcParams['axes.xmargin'] = .12
            plot.rcParams['axes.ymargin'] = .06
            plot.rcParams['legend.borderpad'] = .10
            plot.rcParams['legend.borderaxespad'] = .50

            # plot style (yellow, -- line, dot)
            plot.plot(decile, current_lift, f"{YELLOW_COLOR}{DASHED_LINE}{CIRCLE_MARKER}",
                      label='current', linewidth=line_width)
            if compare_lift:
                plot.plot(decile, compare_lift, f"{GREEN_COLOR}{DASHED_LINE}{CIRCLE_MARKER}",
                          label='compare', linewidth=line_width)

            # axis
            ax = plot.subplot()
            ax.set_xticks(decile)
            ax.grid(axis='y')

            # legend
            if compare_lift:
                leg = ax.legend()
                leg.get_frame().set_edgecolor('b')
                leg.get_frame().set_linewidth(0.0)

            # annotate lines
            def to_decimal_of_list(float_values: List[float]) -> List[Decimal]:
                return [Decimal('%.2f' % f) for f in float_values]

            for d, l, r in zip(decile, current_lift, to_decimal_of_list(current_lift)):
                ax.annotate(r, xy=(d, l),
                            color=YELLOW_COLOR,
                            xytext=(30, np.sign(l) * 3),
                            textcoords="offset points",
                            horizontalalignment=RIGHT,
                            verticalalignment=TOP,
                            weight=BOLD)

            if compare_lift:
                for d, l, r in zip(decile, compare_lift, to_decimal_of_list(compare_lift)):
                    ax.annotate(r, xy=(d, l),
                                color=GREEN_COLOR,
                                xytext=(-5, np.sign(l) * 3),
                                textcoords='offset points',
                                horizontalalignment=RIGHT,
                                verticalalignment=BOTTOM,
                                weight=BOLD)

            plot.xlabel(xlabel=x_label, loc=RIGHT)
            plot.ylabel(ylabel=y_label, loc=TOP)
            plot.title(title, fontweight=BOLD, pad=10)

        plot.show()

    def _check_validation(self):
        if not self._probabilities:
            raise ValueError("Probability values do not exist.")
        if not self._labels:
            raise ValueError("The label value does not exist.")
        if len(self._probabilities) != len(self._labels):
            raise ValueError("The number of probability values and label values is different.")
