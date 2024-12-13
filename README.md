# Automatic on air light using a kasa EP10

## How to use:
1. Plug in light with kasa plug
2. Run `pipenv install` to install dependencies
3. Run `python controller.py setup` to set up plug and follow instructions
4. If everything went well you should have the light connected to the wifi and it will turn on when your camera turns on
5. In the future run `python controller.py` without the setup flag to connect to an existing light

### Todo:

The `main.py` file is a gui light controller that is still a wip

Need to support selecting a specific light if more than one is discovered on the network