# cs2-market-data-engine

# Random project lol

# Setup
Create api keys on steamweb, and put them in keys/STEAMWEB.py named `STEAMWEB_KEY="{yourkey}"`
Create api key on steamapis.com, and put in keys/STEAMAPIS.py named `STEAMAPIS_KEY="{yourkey}"`
to start, run `start.sh`

# Goal
To allow for a market-making panel that uses C++ to calculate a fair value estimate for a given item in steam marketplace. This could further be used to create a model that effectively prices illiquid marketplace items in such a
way that maximizes profit, whilst providing an opportunity to find arbitrage opportunities in the process of calculation.

Here is an example image of the order ladder (currently missing the fair value estimate) of a Chroma 2 case in CS2. [images/example.png]