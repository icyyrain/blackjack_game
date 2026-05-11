# Blackjack Game

Single-player Blackjack against a dealer.

## Setup

```powershell
conda env update -f environment.yml --prune
```

## Test

```powershell
conda run -n blackjack-game pytest
```

## Play in Terminal

```powershell
conda run -n blackjack-game python -m blackjack.cli
```

## Play GUI

```powershell
conda run -n blackjack-game python -m blackjack.gui
```
