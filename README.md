# hammerhome
This is the public repository for my home assistant deployment.

When I first started with HA I was inspired by many of the public configurations found [here](https://github.com/frenck/awesome-home-assistant#public-configurations). If you are just starting out those will be of more use generally speaking, but my repo will be of particular interest to those who wish to use [appdaemon](https://appdaemon.readthedocs.io/en/latest/) and python to control their home.

My most interesting automation is my appdaemon motion lights automation (see [appdaemon-motion-triggered-lights](#appdaemon-motion-triggered-lights) below). I use appdaemon for most of my automations (other than extremely basic ones), so there are a few more in there that may be useful for people learning appdaemon.

## Structure
Important stuff:
- app_daemon - Appdaemon automations
- home-assistant - HA config

Other, less useful stuff:
- alerts - TICKScript alerts, only useful if you push your HA data to influxdb.
- helper_scripts - Various small scripts I use or have used for managing my HA deployment.
- lib - Python representations for a home. Mostly I use this when creating lots of dashboards or automations and want to automate the process.

## Appdaemon motion triggered lights
The motion_lights.py (`app_daemon/conf/apps/motion_lights.py`) automation was the main motivation behind making this repo public, as I wasn't able to find an existing automation to handle all of my requirements for controlling my lights in my home. These requirements include:

- Ability to dynamically add motion sensors and lights without any configuration changes. I often found myself adding new motion sensors to cover blind spots as well as deleting + re-pairing misbehaving devices. **As long as devices follow a naming standard, no changes or restarts are required for them to immediately start working with the existing automations**
- Different room-specific default light brightness settings throughout the day (day/dusk/night), but still allow for manual control of light brightness in each room (i.e., automation won't continually override a manual change)
- Room-specific time of day cutoffs
- Room-specific sun elevation cutoffs
- A single automation that handles all the motion sensors/lights in the house
- Ability to set an input_boolean to disable the automation in a particular room (optional, see `home-assistant/entities/input_boolean/configuration.yaml`)

Several of these requirements can be met using existing public blueprints (when I first started with HA, I used [this](https://community.home-assistant.io/t/turn-on-light-switch-scene-script-or-group-based-on-motion-illuminance-sun-more-conditions/257085) one), but none that I found was able to satisfy all of them, and writing and modifying YAML based automations as a Python developer was extremely cumbersome.

## My setup
I use [zigbee2mqtt](https://www.zigbee2mqtt.io/) as my zigbee interface, and [Aqara motion sensors](https://www.zigbee2mqtt.io/devices/RTCGQ11LM.html#xiaomi-rtcgq11lm). The code should be generic enough (and interacts with HA, not z2m) so it should work fine with other setups, but I haven't tested it.


## Configuration
For general information about configuring and running appdaemon, see the [appdaemon documentation](https://appdaemon.readthedocs.io/en/latest/).

In the apps folder, create a home.yaml file following this structure:

```
areas:
  - name: basement
    lights:
      dusk_brightness: 100
      night_brightness: 100
    rooms:
       - name: basement_stairs
       - name: laundry_room
       - name: game_room
       - name: workshop
  - name: downstairs
    rooms:
       - name: garage
         lights:
           dusk_brightness: 100
           night_brightness: 100
       - name: entry
         lights:
           sun_elevation_below: 40
       - name: mudroom
       - name: kitchen
         lights:
           sun_elevation_below: 40
       - name: dining_room
         lights:
           sun_elevation_below: 40
       - name: living_room
         lights:
           sun_elevation_below: 40
       - name: office
         lights:
           after: "00:00"
           before: "23:59"
           dusk_brightness: 50
       - name: pantry
       - name: mudroom_closet
       - name: downstairs_bathroom
```

See `app_daemon/conf/apps/home.yaml` for a full example.

Within the YAML file, the following optional configuration settings are supported at the area and room level (more specific takes precedence):
- **after**: Time of day after which motion will trigger the lights to go on
- **before**: Time of day before which motion will trigger the lights to go on
- **dusk_brightness**: Brightness to set the lights between 7PM and 9PM
- **night_brightness**: Brightness to set the lights between 9PM and 7AM
- **sun_elevation_below**: Sun elevation below which motion will trigger the lights to go on
- **sun_elevation_above**: Sun elevation above which motion will trigger the lights to go on

In the configuration above, the configuration options for the basement are configured at the area level, while the other rooms are configured at the room level.

## Naming Conventions
The automation will automatically detect motion sensors and lights based on the following naming conventions:
- motion sensors: `binary_sensor.room_name_motion_sensor_<#>` e.g., `binary_sensor.living_room_motion_sensor_0` or `binary_sensor.workshop_motion_sensor_1`
- lights: `light.room_name_lights`, e.g., `light.living_room_lights` or `light.workshop_lights` (personally I configure these as [zigbee2mqtt groups](https://www.zigbee2mqtt.io/guide/usage/groups.html)).

## Timers
Each room should have a timer entity configured. HA handles the timers, which simplifies the code and allows appdaemon to be re-started without impacting light automations. The timer entity should be named `timer.room_name_light_timer` e.g., `timer.living_room_light_timer`. See the `home-assistant/entities/timer/configuration.yaml` file for an example of how to configure a timer entity.

Appdaemon itself does not keep track of the timers, which makes the code much simpler. `motion_lights.py` handles motion events, turning on lights, and starting/re-starting HA timers. `lights_timer_finsihed.py` handles turning off lights when timers finish.

## Overrides
The automation will not turn on lights if the `input_boolean.room_name_light_override` entity is set to `on`. See the `home-assistant/entities/input_boolean/configuration.yaml` for examples of these entities.

