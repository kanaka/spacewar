#!/usr/bin/env python

import ai, objs
import pygame, sys

# Run the fitness testing faster than normal
objs.standalone_frame_rate = 80

ai.load_game_resources()

print ai.dna_pool

objs.main()
