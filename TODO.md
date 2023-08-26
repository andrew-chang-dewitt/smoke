TODO
===

- [ ] Refactor fan controller to be managed by an async worker
- [ ] Refactor probe reading loop to be managed by an async worker that pushes/yields on each new read?
- [ ] Refactor maintain algorithm to not actually contain the loop but instead just be a function that runs once, taking the target, history, fan worker, & latest probe data and make a single decision on the fan speed each time it runs
- [ ] Move that control loop that was in maintain to main?

All this sets us up to the then also do the following for the next feature pushes:

- [ ] [optional] Add fan speed readout? This would just be a simple off/slow/medium/fast readout--not a tach as the current fan hardware has no tach output
- [ ] create small api server that...
  - [ ] feeds temp (& fan if above is impl'd) data to a client via a websocket
  - [ ] allows turning on and off probes via REST endpoints
  - [ ] allows turning on and off controller loop via REST endpoints
  - [ ] allows setting target temp via REST endpoint

Which then allows us to do the GUI part:

- [ ] GUI for turning on and off fan controller
- [ ] GUI for setting target temp
- [ ] GUI for turning on and off probes
- [ ] View for seeing all current temps for all active probes
- [ ] Graph view for 1 (or more?) selected probe(s?)

Later it'd be nice to:

- [ ] Save history in cloud db & browse it by cook session in web client
- [ ] Name probes in GUI and have that persist between client sessions and cook sessions
- [ ] Tweak fan controller algo for a "Turbo" mode like Joule Turbo
