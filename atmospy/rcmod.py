import seaborn as sns

__all__ = ["set_theme"]

def set_theme(context="notebook", style='ticks', palette='colorblind', 
              font='sans-serif', font_scale=1., color_codes=True, rc=None):
    """Change the look and feel of your plots with one simple function.
    
    This is a simple pass-through function to the Seaborn function of the 
    same name, but with different default parameters. For complete information 
    and a better description that I can provide, please see the Seaborn docs
    `here <https://seaborn.pydata.org/generated/seaborn.set_theme.html#seaborn.set_theme>`_.
    
    This mostly passes down to the seaborn function of the same name, but with a 
    few opinions mixed in.

    Parameters
    ----------
    context : string or dict, optional
        Set the scaling parameter for different environments, by default "notebook"
    style : string or dict, optional
        Set the axes style parameters, by default 'white'
    palette : string or sequence, optional
        Set the color palette, by default 'colorblind'
    font : string, optional
        Set the font family, by default 'sans-serif'. See the 
        matplotlib font manager for more information.
    font_scale : float, optional
        Independently scale the font size, by default 1
    color_codes : bool, optional
        If `True`, remap the shorthand color codes assuming you are 
        using a seaborn palette, by default True
    rc : dict or None, optional
        Pass through a dictionary of rc parameter mappings to override 
        the defaults, by default None
        
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
