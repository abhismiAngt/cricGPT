import matplotlib.pyplot as plt

def bar_chart(df, x_col, y_col, title="", xlabel="", ylabel="", figsize=(8, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(df[x_col], df[y_col])
    ax.set_title(title)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)
    plt.setp(ax.get_xticklabels(), rotation=30)
    plt.tight_layout()
    return fig


def line_chart(df, x_col, y_col, title="", xlabel="", ylabel="", figsize=(8, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df[x_col], df[y_col], marker="o")
    ax.set_title(title)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)
    ax.grid(True)
    plt.tight_layout()
    return fig


def pie_chart(labels, values, title="", figsize=(6, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.set_title(title)
    plt.tight_layout()
    return fig
