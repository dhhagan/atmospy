import seaborn as sns

__all__ = ["set_theme"]

def set_theme(context="notebook", style='ticks', palette='colorblind', 
              font='sans-serif', font_scale=1, color_codes=True, rc=None):
    """_summary_
    
    This mostly passes down to the seaborn function of the same name, but with a 
    few opinions mixed in.

    Parameters
    ----------
    context : str, optional
        _description_, by default "notebook"
    style : str, optional
        _description_, by default 'white'
    palette : str, optional
        _description_, by default 'colorblind'
    font : str, optional
        _description_, by default 'sans-serif'
    font_scale : int, optional
        _description_, by default 1
    color_codes : bool, optional
        _description_, by default True
    rc : _type_, optional
        _description_, by default None
    """
    default_rcparams = {
        "mathtext.default": "regular"
    }
    
    if rc is not None:
        rc = dict(default_rcparams, **rc)
    else:
        rc = default_rcparams

    sns.set_theme(
        context=context, style=style, palette=palette,
        font=font, font_scale=font_scale, color_codes=color_codes, rc=rc
    )
