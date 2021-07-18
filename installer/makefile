# ----------------------------
# Makefile Options
# ----------------------------

NAME ?= PYINST
ICON ?= icon.png
DESCRIPTION ?= "Python++ Installer"
COMPRESSED ?= NO
ARCHIVED ?= NO

CFLAGS ?= -Wall -Wextra -Oz
CXXFLAGS ?= -Wall -Wextra -Oz

# ----------------------------

more_all: all appvars

ifndef CEDEV
$(error CEDEV environment path variable is not set)
endif

include $(CEDEV)/meta/makefile.mk
