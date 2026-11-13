'''Create only the US benchmark using the common production-figure settings.'''

from model_vs_data import apply_course_style, plot_us_benchmark


def main() -> None:
    apply_course_style()
    print(plot_us_benchmark())


if __name__ == '__main__':
    main()
