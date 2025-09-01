var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => {
  __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
  return value;
};
var __accessCheck = (obj, member, msg) => {
  if (!member.has(obj))
    throw TypeError("Cannot " + msg);
};
var __privateGet = (obj, member, getter) => {
  __accessCheck(obj, member, "read from private field");
  return getter ? getter.call(obj) : member.get(obj);
};
var __privateAdd = (obj, member, value) => {
  if (member.has(obj))
    throw TypeError("Cannot add the same private member more than once");
  member instanceof WeakSet ? member.add(obj) : member.set(obj, value);
};
var __privateSet = (obj, member, value, setter) => {
  __accessCheck(obj, member, "write to private field");
  setter ? setter.call(obj, value) : member.set(obj, value);
  return value;
};
var __privateMethod = (obj, member, method) => {
  __accessCheck(obj, member, "access private method");
  return method;
};

// data/gametests/src/index.ts
import { world as world15, system as system17 } from "@minecraft/server";

// data/gametests/src/craftBuild/index.ts
import {
  world as world9,
  system as system10,
  ItemStack as ItemStack4,
  StructureAnimationMode as StructureAnimationMode2,
  ItemLockMode,
  StructureRotation as StructureRotation2,
  LocationInUnloadedChunkError
} from "@minecraft/server";

// data/gametests/src/dev_tools/itemTransfer.js
import { world, system, ItemStack } from "@minecraft/server";
function date() {
  const date2 = new Date(Date.now());
  const ms = date2.getMilliseconds().toString().padStart(3, "0");
  return `${date2.toLocaleString().replace(" AM", `.${ms} AM`).replace(" PM", `.${ms} PM`)}`;
}
var _validNamespace, _queuedKeys, _settings, _quickAccess, _queuedValues, _dimension, _sL, _load, load_fn, _save, save_fn, _queueSaving, queueSaving_fn, _romSave, romSave_fn;
var QIDB = class {
  /**
   * @param {string} namespace The unique namespace for the database keys.
   * @param {number} cacheSize Quick the max amount of keys to keep quickly accessible. A small size can couse lag on frequent iterated usage, a large number can cause high hardware RAM usage.
   * @param {number} saveRate the background saves per tick, (high performance impact) saveRate1 is 20 keys per second
   */
  constructor(namespace = "", cacheSize = 100, saveRate = 1) {
    __privateAdd(this, _load);
    __privateAdd(this, _save);
    __privateAdd(this, _queueSaving);
    __privateAdd(this, _romSave);
    __publicField(this, "logs");
    __privateAdd(this, _validNamespace, void 0);
    __privateAdd(this, _queuedKeys, void 0);
    __privateAdd(this, _settings, void 0);
    __privateAdd(this, _quickAccess, void 0);
    __privateAdd(this, _queuedValues, void 0);
    __privateAdd(this, _dimension, void 0);
    __privateAdd(this, _sL, void 0);
    system.run(() => {
      const self = this;
      __privateSet(this, _settings, {
        namespace
      });
      __privateSet(this, _queuedKeys, []);
      __privateSet(this, _queuedValues, []);
      __privateSet(this, _quickAccess, /* @__PURE__ */ new Map());
      __privateSet(this, _validNamespace, /^[A-Za-z0-9_]*$/.test(__privateGet(this, _settings).namespace));
      __privateSet(this, _dimension, world.getDimension("overworld"));
      this.logs = {
        startUp: true,
        save: true,
        load: true,
        set: true,
        get: true,
        has: true,
        delete: true,
        clear: true,
        values: true,
        keys: true
      };
      function startLog() {
        console.log(
          `initialized successfully.\xA7r namespace: ${__privateGet(self, _settings).namespace} \xA7r${date()} `
        );
      }
      const VALID_NAMESPACE_ERROR = new Error(`\xA7c${namespace} isn't a valid namespace \xA7r${date()}`);
      let sl = world.scoreboard.getObjective("qidb");
      __privateGet(this, _sL);
      const player = world.getPlayers()[0];
      if (!__privateGet(this, _validNamespace))
        throw VALID_NAMESPACE_ERROR;
      if (player)
        if (!sl || sl?.hasParticipant("x") === false) {
          if (!sl)
            sl = world.scoreboard.addObjective("qidb");
          sl.setScore("x", player.location.x);
          sl.setScore("z", player.location.z);
          __privateSet(this, _sL, { x: sl.getScore("x"), y: 318, z: sl.getScore("z") });
          __privateGet(this, _dimension).runCommand(`/tickingarea add ${__privateGet(this, _sL).x} 319 ${__privateGet(this, _sL).z} ${__privateGet(this, _sL).x} 318 ${__privateGet(this, _sL).z} storagearea`);
          startLog();
        } else {
          __privateSet(this, _sL, { x: sl.getScore("x"), y: 318, z: sl.getScore("z") });
          startLog();
        }
      world.afterEvents.playerSpawn.subscribe(({ player: player2, initialSpawn }) => {
        if (!__privateGet(this, _validNamespace))
          throw VALID_NAMESPACE_ERROR;
        if (!initialSpawn)
          return;
        if (!sl || sl?.hasParticipant("x") === false) {
          if (!sl)
            sl = world.scoreboard.addObjective("qidb");
          sl.setScore("x", player2.location.x);
          sl.setScore("z", player2.location.z);
          __privateSet(this, _sL, { x: sl.getScore("x"), y: 318, z: sl.getScore("z") });
          __privateGet(this, _dimension).runCommand(`/tickingarea add ${__privateGet(this, _sL).x} 319 ${__privateGet(this, _sL).z} ${__privateGet(this, _sL).x} 318 ${__privateGet(this, _sL).z} storagearea`);
          startLog();
        } else {
          __privateSet(this, _sL, { x: sl.getScore("x"), y: 318, z: sl.getScore("z") });
          startLog();
        }
      });
      let show = true;
      let runId;
      let lastam;
      system.runInterval(() => {
        const diff = __privateGet(self, _quickAccess).size - cacheSize;
        if (diff > 0) {
          for (let i = 0; i < diff; i++) {
            __privateGet(self, _quickAccess).delete(__privateGet(self, _quickAccess).keys().next()?.value);
          }
        }
        if (__privateGet(self, _queuedKeys).length) {
          if (!runId) {
            log3();
            runId = system.runInterval(() => {
              log3();
            }, 120);
          }
          show = false;
          const k = Math.min(saveRate, __privateGet(this, _queuedKeys).length);
          for (let i = 0; i < k; i++) {
            __privateMethod(this, _romSave, romSave_fn).call(this, __privateGet(this, _queuedKeys)[0], __privateGet(this, _queuedValues)[0]);
            __privateGet(this, _queuedKeys).shift();
            __privateGet(this, _queuedValues).shift();
          }
        } else if (runId) {
          system.clearRun(runId);
          runId = void 0;
          show == false && this.logs.save == true && console.log(`\xA7aSaved, You can now close the world safely. \xA7r${date()}`);
          show = true;
          return;
        } else
          return;
      }, 1);
      function log3() {
        const abc = (-(__privateGet(self, _queuedKeys).length - lastam) / 6).toFixed(0) || "//";
        self.logs.save == true && console.log(`\xA7eSaving, Dont close the world.
\xA7r[Stats]-\xA7eRemaining: ${__privateGet(self, _queuedKeys).length} keys | speed: ${abc} keys/s \xA7r${date()}`);
        lastam = __privateGet(self, _queuedKeys).length;
      }
      world.beforeEvents.playerLeave.subscribe(() => {
        if (__privateGet(this, _queuedKeys).length && world.getPlayers().length < 2) {
          console.error(
            `



\xA7cWorld closed too early, items not saved correctly.  

Namespace: ${__privateGet(this, _settings).namespace}
Lost Keys amount: ${__privateGet(this, _queuedKeys).length} \xA7r${date()}



`
          );
        }
      });
    });
  }
  /**
   * Sets a value as a key in the item database.
   * @param {string} key The unique identifier of the value.
   * @param {ItemStack[] | ItemStack} value The `ItemStack[]` or `itemStack` value to set.
   * @throws Throws if `value` is an array that has more than 255 items.
   */
  set(key, value) {
    if (!__privateGet(this, _validNamespace))
      throw new Error(`\xA7cInvalid name: <${__privateGet(this, _settings).namespace}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    if (!/^[A-Za-z0-9_]*$/.test(key))
      throw new Error(`\xA7cInvalid name: <${key}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    const time = Date.now();
    key = __privateGet(this, _settings).namespace + ":" + key;
    if (Array.isArray(value)) {
      if (value.length > 255)
        throw new Error(`\xA7cOut of range: <${key}> has more than 255 ItemStacks \xA7r${date()}`);
      world.setDynamicProperty(key, true);
    } else {
      world.setDynamicProperty(key, false);
    }
    __privateGet(this, _quickAccess).set(key, value);
    if (__privateGet(this, _queuedKeys).includes(key)) {
      const i = __privateGet(this, _queuedKeys).indexOf(key);
      __privateGet(this, _queuedValues).splice(i, 1);
      __privateGet(this, _queuedKeys).splice(i, 1);
    }
    __privateMethod(this, _queueSaving, queueSaving_fn).call(this, key, value);
    this.logs.set == true && console.log(`\xA7aSet key <${key}> succesfully. ${Date.now() - time}ms \xA7r${date()}`);
  }
  /**
   * Gets the value of a key from the item database.
   * @param {string} key The identifier of the value.
   * @returns {ItemStack | ItemStack[]} The `ItemStack` | `ItemStack[]` saved as `key`
   * @throws Throws if the key doesn't exist.
   */
  get(key) {
    if (!__privateGet(this, _validNamespace))
      throw new Error(`\xA7cInvalid name: <${__privateGet(this, _settings).namespace}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    if (!/^[A-Za-z0-9_]*$/.test(key))
      throw new Error(`\xA7cInvalid name: <${key}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    const time = Date.now();
    key = __privateGet(this, _settings).namespace + ":" + key;
    if (__privateGet(this, _quickAccess).has(key)) {
      this.logs.get == true && console.log(`\xA7aGot key <${key}> succesfully. ${Date.now() - time}ms \xA7r${date()}`);
      return __privateGet(this, _quickAccess).get(key);
    }
    const structure = world.structureManager.get(key);
    if (!structure)
      throw new Error(`\xA7cThe key < ${key} > doesn't exist.`);
    const { canStr, inv } = __privateMethod(this, _load, load_fn).call(this, key);
    const items = [];
    for (let i = 0; i < 256; i++)
      items.push(inv.getItem(i));
    for (let i = 255; i >= 0; i--)
      if (!items[i])
        items.pop();
      else
        break;
    __privateMethod(this, _save, save_fn).call(this, key, canStr);
    this.logs.get == true && console.log(`\xA7aGot items from <${key}> succesfully. ${Date.now() - time}ms \xA7r${date()}`);
    if (world.getDynamicProperty(key)) {
      __privateGet(this, _quickAccess).set(key, items);
      return items;
    } else {
      __privateGet(this, _quickAccess).set(key, items[0]);
      return items[0];
    }
  }
  /**
   * Checks if a key exists in the item database.
   * @param {string} key The identifier of the value.
   * @returns {boolean}`true` if the key exists, `false` if the key doesn't exist.
   */
  has(key) {
    if (!__privateGet(this, _validNamespace))
      throw new Error(`\xA7cInvalid name: <${__privateGet(this, _settings).namespace}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    if (!/^[A-Za-z0-9_]*$/.test(key))
      throw new Error(`\xA7cInvalid name: <${key}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    const time = Date.now();
    key = __privateGet(this, _settings).namespace + ":" + key;
    const exist = __privateGet(this, _quickAccess).has(key) || world.structureManager.get(key);
    this.logs.has == true && console.log(`\xA7aFound key <${key}> succesfully. ${Date.now() - time}ms \xA7r${date()}`);
    if (exist)
      return true;
    else
      return false;
  }
  /**
   * Deletes a key from the item database.
   * @param {string} key The identifier of the value.
  								* @throws Throws if the key doesn't exist.
  								*/
  delete(key) {
    if (!__privateGet(this, _validNamespace))
      throw new Error(`\xA7cInvalid name: <${__privateGet(this, _settings).namespace}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    if (!/^[A-Za-z0-9_]*$/.test(key))
      throw new Error(`\xA7cInvalid name: <${key}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    const time = Date.now();
    key = __privateGet(this, _settings).namespace + ":" + key;
    if (__privateGet(this, _quickAccess).has(key))
      __privateGet(this, _quickAccess).delete(key);
    const structure = world.structureManager.get(key);
    if (structure)
      world.structureManager.delete(key), world.setDynamicProperty(key, null);
    else
      throw new Error(`\xA7cThe key <${key}> doesn't exist. \xA7r${date()}`);
    this.logs.delete == true && console.log(`\xA7aDeleted key <${key}> succesfully. ${Date.now() - time}ms \xA7r${date()}`);
  }
  /**
   * Gets all the keys of your namespace from item database.
   * @return {string[]} All the keys as an array of strings.
  										*/
  keys() {
    if (!__privateGet(this, _validNamespace))
      throw new Error(`\xA7cInvalid name: <${__privateGet(this, _settings).namespace}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    const allIds = world.getDynamicPropertyIds();
    const ids = [];
    allIds.filter((id) => id.startsWith(__privateGet(this, _settings).namespace + ":")).forEach((id) => ids.push(id.replace(__privateGet(this, _settings).namespace + ":", "")));
    this.logs.keys == true && console.log(`\xA7aGot the list of all the ${ids.length} keys. \xA7r${date()}`);
    return ids;
  }
  /**
   * Gets all the keys of your namespace from item database (takes some time if values aren't alredy loaded in quickAccess).
   * @return {ItemStack[][]} All the values as an array of ItemStack or ItemStack[].
  												*/
  values() {
    if (!__privateGet(this, _validNamespace))
      throw new Error(`\xA7cInvalid name: <${__privateGet(this, _settings).namespace}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    const time = Date.now();
    const allIds = world.getDynamicPropertyIds();
    const values = [];
    const filtered = allIds.filter((id) => id.startsWith(__privateGet(this, _settings).namespace + ":")).map((id) => id.replace(__privateGet(this, _settings).namespace + ":", ""));
    for (const key of filtered) {
      values.push(this.get(key));
    }
    this.logs.values == true && console.log(`\xA7aGot the list of all the ${values.length} values. ${Date.now() - time}ms \xA7r${date()}`);
    return values;
  }
  /**
   * Clears all, CAN NOT REWIND.
   */
  clear() {
    if (!__privateGet(this, _validNamespace))
      throw new Error(`\xA7cInvalid name: <${__privateGet(this, _settings).namespace}>. accepted char: A-Z a-z 0-9 _ \xA7r${date()}`);
    const time = Date.now();
    const allIds = world.getDynamicPropertyIds();
    const filtered = allIds.filter((id) => id.startsWith(__privateGet(this, _settings).namespace + ":")).map((id) => id.replace(__privateGet(this, _settings).namespace + ":", ""));
    for (const key of filtered) {
      this.delete(key);
    }
    this.logs.clear == true && console.log(`\xA7aCleared, deleted ${filtered.length} values. ${Date.now() - time}ms \xA7r${date()}`);
  }
};
_validNamespace = new WeakMap();
_queuedKeys = new WeakMap();
_settings = new WeakMap();
_quickAccess = new WeakMap();
_queuedValues = new WeakMap();
_dimension = new WeakMap();
_sL = new WeakMap();
_load = new WeakSet();
load_fn = function(key) {
  if (key.length > 30)
    throw new Error(`\xA7cOut of range: <${key}> has more than 30 characters \xA7r${date()}`);
  let canStr = false;
  try {
    world.structureManager.place(key, __privateGet(this, _dimension), __privateGet(this, _sL), { includeEntities: true });
    canStr = true;
  } catch {
    __privateGet(this, _dimension).spawnEntity("5fs_cb:item_storage", __privateGet(this, _sL));
  }
  const entities = __privateGet(this, _dimension).getEntities({ location: __privateGet(this, _sL), type: "5fs_cb:item_storage" });
  if (entities.length > 1)
    entities.forEach((e, index) => entities[index + 1]?.remove());
  const entity = entities[0];
  const inv = entity.getComponent("inventory").container;
  this.logs.load == true && console.log(`\xA7aLoaded entity <${key}> \xA7r${date()}`);
  return { canStr, inv };
};
_save = new WeakSet();
save_fn = async function(key, canStr) {
  if (canStr)
    world.structureManager.delete(key);
  world.structureManager.createFromWorld(key, __privateGet(this, _dimension), __privateGet(this, _sL), __privateGet(this, _sL), { saveMode: "World", includeEntities: true });
  const entities = __privateGet(this, _dimension).getEntities({ location: __privateGet(this, _sL), type: "5fs_cb:item_storage" });
  entities.forEach((e) => e.remove());
};
_queueSaving = new WeakSet();
queueSaving_fn = async function(key, value) {
  __privateGet(this, _queuedKeys).push(key);
  __privateGet(this, _queuedValues).push(value);
};
_romSave = new WeakSet();
romSave_fn = async function(key, value) {
  const { canStr, inv } = __privateMethod(this, _load, load_fn).call(this, key);
  if (!value)
    for (let i = 0; i < 256; i++)
      inv.setItem(i, void 0), world.setDynamicProperty(key, null);
  if (Array.isArray(value)) {
    try {
      for (let i = 0; i < 256; i++)
        inv.setItem(i, value[i] || void 0);
    } catch {
      throw new Error(`\xA7cInvalid value type. supported: ItemStack | ItemStack[] | undefined \xA7r${date()}`);
    }
    world.setDynamicProperty(key, true);
  } else {
    try {
      inv.setItem(0, value), world.setDynamicProperty(key, false);
    } catch {
      throw new Error(`\xA7cInvalid value type. supported: ItemStack | ItemStack[] | undefined \xA7r${date()}`);
    }
  }
  __privateMethod(this, _save, save_fn).call(this, key, canStr);
};

// data/gametests/node_modules/@bedrock-oss/bedrock-boost/dist/index.mjs
import { Direction } from "@minecraft/server";
import { system as system2, world as world2 } from "@minecraft/server";
import { system as system22 } from "@minecraft/server";
import { BlockPermutation, world as world22 } from "@minecraft/server";
import { world as world3 } from "@minecraft/server";
import { Player } from "@minecraft/server";
import { system as system3 } from "@minecraft/server";
import { system as system4 } from "@minecraft/server";
import {
  system as system5,
  world as world4
} from "@minecraft/server";
import { Player as Player2, system as system6, world as world5 } from "@minecraft/server";
import {
  InputPermissionCategory
} from "@minecraft/server";
import { system as system7 } from "@minecraft/server";
import { Direction as Direction2 } from "@minecraft/server";
import { StructureSaveMode, world as world6 } from "@minecraft/server";
import { EntityEquippableComponent, EquipmentSlot, ItemDurabilityComponent, ItemEnchantableComponent } from "@minecraft/server";
var _a;
var ChatColor = (_a = class {
  /**
   * Class ChatColor Constructor.
   * @param code - The color code as a string.
   * @param color - The color code as a hexadecimal number. Can be undefined.
   */
  constructor(code, color) {
    __publicField(this, "r");
    __publicField(this, "g");
    __publicField(this, "b");
    this.code = code;
    this.color = color;
    if (color) {
      this.r = color >> 16 & 255;
      this.g = color >> 8 & 255;
      this.b = color & 255;
    }
  }
  /**
   * Returns the string representation of the ChatColor instance,
   * which includes the PREFIX followed by the color code.
   * @returns A string representing the ChatColor instance
   */
  toString() {
    return _a.PREFIX + this.code;
  }
  /**
   * Returns the color code of the ChatColor instance.
   * @returns The color code of this ChatColor instance.
   */
  toRGB() {
    return this.color;
  }
  /**
   * Returns the hexadecimal string representation of the color code
   * @returns {string | undefined} The hexadecimal representation of the color.
   */
  toHex() {
    return this.color?.toString(16);
  }
  /**
   * Retrieve the value of the red component.
   *
   * @returns {number | undefined} The value of the red component, or undefined if it is not set.
   */
  getRed() {
    return this.r;
  }
  /**
   * Retrieves the green value of the current color.
   *
   * @returns {number | undefined} The green value of the color, or undefined if it is not set.
   */
  getGreen() {
    return this.g;
  }
  /**
   * Retrieves the blue value of a color.
   *
   * @returns The blue value of the color.
   * @type {number | undefined}
   */
  getBlue() {
    return this.b;
  }
  /**
   * Retrieves the format code associated with the chat color.
   *
   * @returns {string} The format code of the chat color.
   */
  getCode() {
    return this.code;
  }
  /**
   * Removes color codes from the specified string
   * @param str - The string from which color codes will be removed.
   * @returns The string cleared from color codes.
   */
  static stripColor(str) {
    return str.replace(/§[0-9a-u]/g, "");
  }
  /**
   * Finds the closest ChatColor code for the given RGB values
   * @param r - Red part of the color.
   * @param g - Green part of the color.
   * @param b - Blue part of the color.
   * @returns The closest ChatColor for the given RGB values.
   */
  static findClosestColor(r, g, b) {
    let minDistance = Number.MAX_VALUE;
    let closestColor = _a.WHITE;
    for (const color of _a.ALL_COLORS) {
      if (color.r && color.g && color.b) {
        const distance = Math.sqrt(Math.pow(color.r - r, 2) + Math.pow(color.g - g, 2) + Math.pow(color.b - b, 2));
        if (distance < minDistance) {
          minDistance = distance;
          closestColor = color;
        }
      }
    }
    return closestColor;
  }
}, /**
 * Black color code. (0)
 */
__publicField(_a, "BLACK", new _a("0", 0)), /**
 * Dark blue color code. (1)
 */
__publicField(_a, "DARK_BLUE", new _a("1", 170)), /**
 * Dark green color code. (2)
 */
__publicField(_a, "DARK_GREEN", new _a("2", 43520)), /**
 * Dark aqua color code. (3)
 */
__publicField(_a, "DARK_AQUA", new _a("3", 43690)), /**
 * Dark red color code. (4)
 */
__publicField(_a, "DARK_RED", new _a("4", 11141120)), /**
 * Dark purple color code. (5)
 */
__publicField(_a, "DARK_PURPLE", new _a("5", 11141290)), /**
 * Gold color code. (6)
 */
__publicField(_a, "GOLD", new _a("6", 16755200)), /**
 * Gray color code. (7)
 */
__publicField(_a, "GRAY", new _a("7", 11184810)), /**
 * Dark gray color code. (8)
 */
__publicField(_a, "DARK_GRAY", new _a("8", 5592405)), /**
 * Blue color code. (9)
 */
__publicField(_a, "BLUE", new _a("9", 5592575)), /**
 * Green color code. (a)
 */
__publicField(_a, "GREEN", new _a("a", 5635925)), /**
 * Aqua color code. (b)
 */
__publicField(_a, "AQUA", new _a("b", 5636095)), /**
 * Red color code. (c)
 */
__publicField(_a, "RED", new _a("c", 16733525)), /**
 * Light purple color code. (d)
 */
__publicField(_a, "LIGHT_PURPLE", new _a("d", 16733695)), /**
 * Yellow color code. (e)
 */
__publicField(_a, "YELLOW", new _a("e", 16777045)), /**
 * White color code. (f)
 */
__publicField(_a, "WHITE", new _a("f", 16777215)), /**
 * MineCoin gold color code. (g)
 */
__publicField(_a, "MINECOIN_GOLD", new _a("g", 14603781)), /**
 * Material quartz color code. (h)
 */
__publicField(_a, "MATERIAL_QUARTZ", new _a("h", 14931153)), /**
 * Material iron color code. (i)
 */
__publicField(_a, "MATERIAL_IRON", new _a("i", 13552330)), /**
 * Material netherite color code. (j)
 */
__publicField(_a, "MATERIAL_NETHERITE", new _a("j", 4471355)), /**
 * Material redstone color code. (m)
 */
__publicField(_a, "MATERIAL_REDSTONE", new _a("m", 9901575)), /**
 * Material copper color code. (n)
 */
__publicField(_a, "MATERIAL_COPPER", new _a("n", 11823181)), /**
 * Material gold color code. (p)
 */
__publicField(_a, "MATERIAL_GOLD", new _a("p", 14594349)), /**
 * Material emerald color code. (q)
 */
__publicField(_a, "MATERIAL_EMERALD", new _a("q", 1155126)), /**
 * Material diamond color code. (s)
 */
__publicField(_a, "MATERIAL_DIAMOND", new _a("s", 2931368)), /**
 * Material lapis color code. (t)
 */
__publicField(_a, "MATERIAL_LAPIS", new _a("t", 2181499)), /**
 * Material amethyst color code. (u)
 */
__publicField(_a, "MATERIAL_AMETHYST", new _a("u", 10116294)), /**
 * Obfuscated color code. (k)
 */
__publicField(_a, "OBFUSCATED", new _a("k")), /**
 * Bold color code. (l)
 */
__publicField(_a, "BOLD", new _a("l")), /**
 * Italic color code. (o)
 */
__publicField(_a, "ITALIC", new _a("o")), /**
 * Reset color code. (r)
 */
__publicField(_a, "RESET", new _a("r")), /**
 * All available color codes.
 */
__publicField(_a, "VALUES", [
  _a.BLACK,
  _a.DARK_BLUE,
  _a.DARK_GREEN,
  _a.DARK_AQUA,
  _a.DARK_RED,
  _a.DARK_PURPLE,
  _a.GOLD,
  _a.GRAY,
  _a.DARK_GRAY,
  _a.BLUE,
  _a.GREEN,
  _a.AQUA,
  _a.RED,
  _a.LIGHT_PURPLE,
  _a.YELLOW,
  _a.WHITE,
  _a.MINECOIN_GOLD,
  _a.MATERIAL_QUARTZ,
  _a.MATERIAL_IRON,
  _a.MATERIAL_NETHERITE,
  _a.MATERIAL_REDSTONE,
  _a.MATERIAL_COPPER,
  _a.MATERIAL_GOLD,
  _a.MATERIAL_EMERALD,
  _a.MATERIAL_DIAMOND,
  _a.MATERIAL_LAPIS,
  _a.MATERIAL_AMETHYST,
  _a.OBFUSCATED,
  _a.BOLD,
  _a.ITALIC,
  _a.RESET
]), /**
 * All available color codes excluding the formatting codes.
 */
__publicField(_a, "ALL_COLORS", [
  _a.BLACK,
  _a.DARK_BLUE,
  _a.DARK_GREEN,
  _a.DARK_AQUA,
  _a.DARK_RED,
  _a.DARK_PURPLE,
  _a.GOLD,
  _a.GRAY,
  _a.DARK_GRAY,
  _a.BLUE,
  _a.GREEN,
  _a.AQUA,
  _a.RED,
  _a.LIGHT_PURPLE,
  _a.YELLOW,
  _a.WHITE,
  _a.MINECOIN_GOLD,
  _a.MATERIAL_QUARTZ,
  _a.MATERIAL_IRON,
  _a.MATERIAL_NETHERITE,
  _a.MATERIAL_REDSTONE,
  _a.MATERIAL_COPPER,
  _a.MATERIAL_GOLD,
  _a.MATERIAL_EMERALD,
  _a.MATERIAL_DIAMOND,
  _a.MATERIAL_LAPIS,
  _a.MATERIAL_AMETHYST
]), /**
 * PREFIX is the section sign (§) used in Minecraft color codes.
 */
__publicField(_a, "PREFIX", "\xA7"), _a);
var _a2;
var ColorJSON = (_a2 = class {
  constructor() {
    // Tokens
    __publicField(this, "OpenObject", "{");
    __publicField(this, "CloseObject", "}");
    __publicField(this, "OpenArray", "[");
    __publicField(this, "CloseArray", "]");
    __publicField(this, "Comma", ",");
    __publicField(this, "KeyValueSeparator", ":");
    __publicField(this, "StringDelimiter", '"');
    __publicField(this, "KeyDelimiter", "");
    __publicField(this, "Indent", "  ");
    __publicField(this, "NewLine", "\n");
    __publicField(this, "Space", " ");
    // Threshold for inline representation
    __publicField(this, "InlineThreshold", 60);
    // Maximum depth to which objects will be traversed
    __publicField(this, "MaxDepth", 1);
    // Whether to include class names
    __publicField(this, "IncludeClassNames", true);
    // Values
    __publicField(this, "FunctionValue", "\u0192");
    __publicField(this, "NullValue", "null");
    __publicField(this, "UndefinedValue", "undefined");
    __publicField(this, "TrueValue", "true");
    __publicField(this, "FalseValue", "false");
    __publicField(this, "CycleValue", "[...cycle...]");
    __publicField(this, "TruncatedObjectValue", "{...}");
    // Colors
    __publicField(this, "OpenCloseObjectColor", ChatColor.YELLOW);
    __publicField(this, "OpenCloseArrayColor", ChatColor.AQUA);
    __publicField(this, "NumberColor", ChatColor.DARK_AQUA);
    __publicField(this, "StringColor", ChatColor.DARK_GREEN);
    __publicField(this, "BooleanColor", ChatColor.GOLD);
    __publicField(this, "NullColor", ChatColor.GOLD);
    __publicField(this, "KeyColor", ChatColor.GRAY);
    __publicField(this, "EscapeColor", ChatColor.GOLD);
    __publicField(this, "FunctionColor", ChatColor.GRAY);
    __publicField(this, "ClassColor", ChatColor.GRAY);
    __publicField(this, "ClassStyle", ChatColor.BOLD);
    __publicField(this, "CycleColor", ChatColor.DARK_RED);
  }
  static createPlain() {
    const plain = new _a2();
    plain.OpenCloseObjectColor = "";
    plain.OpenCloseArrayColor = "";
    plain.NumberColor = "";
    plain.StringColor = "";
    plain.BooleanColor = "";
    plain.NullColor = "";
    plain.KeyColor = "";
    plain.EscapeColor = "";
    plain.FunctionColor = "";
    plain.ClassColor = "";
    plain.ClassStyle = "";
    plain.CycleColor = "";
    return plain;
  }
  /**
   * Transforms a value into a chat-friendly, colored JSON representation.
   * @param value - The value to transform.
   */
  stringify(value) {
    return this.stringifyValue(value, {
      indentLevel: 0,
      visited: /* @__PURE__ */ new WeakSet()
    });
  }
  /**
   * Transforms a string into a JSON representation.
   * @param value - The string to transform.
   */
  stringifyString(value) {
    return this.StringColor + this.StringDelimiter + this.escapeString(value) + this.StringDelimiter + ChatColor.RESET;
  }
  /**
   * Transforms a number into a JSON representation.
   * @param value - The number to transform.
   */
  stringifyNumber(value) {
    return this.NumberColor + value.toString() + ChatColor.RESET;
  }
  /**
   * Transforms a boolean into a JSON representation.
   * @param value - The boolean to transform.
   */
  stringifyBoolean(value) {
    return this.BooleanColor + (value ? this.TrueValue : this.FalseValue) + ChatColor.RESET;
  }
  /**
   * Transforms a function into a JSON representation.
   * @param value - The function to transform.
   */
  // eslint-disable-next-line @typescript-eslint/ban-types
  stringifyFunction(value) {
    return this.FunctionColor + this.FunctionValue + ChatColor.RESET;
  }
  /**
   * Returns a null JSON representation.
   */
  stringifyNull() {
    return this.NullColor + this.NullValue + ChatColor.RESET;
  }
  /**
   * Returns an undefined JSON representation.
   */
  stringifyUndefined() {
    return this.NullColor + this.UndefinedValue + ChatColor.RESET;
  }
  /**
   * Returns a cycle JSON representation.
   */
  stringifyCycle() {
    return this.CycleColor + this.CycleValue + ChatColor.RESET;
  }
  /**
   * Transforms an array into a JSON representation.
   * @param value - The array to transform.
   * @param indentLevel - The indentation level for pretty-printing.
   */
  stringifyArray(value, ctx) {
    const indentSpace = this.Indent.repeat(ctx.indentLevel);
    if (value.length === 0) {
      return this.OpenCloseArrayColor + this.OpenArray + this.CloseArray + ChatColor.RESET;
    }
    let result = this.OpenCloseArrayColor + this.OpenArray + ChatColor.RESET + this.NewLine;
    let compactResult = this.OpenCloseArrayColor + this.OpenArray + ChatColor.RESET;
    value.forEach((item, index) => {
      result += indentSpace + this.Indent + this.stringifyValue(item, this.indent(ctx));
      result += index < value.length - 1 ? this.Comma + this.NewLine : this.NewLine;
      compactResult += this.stringifyValue(item, this.indent(ctx));
      compactResult += index < value.length - 1 ? this.Comma + this.Space : "";
    });
    result += indentSpace + this.OpenCloseArrayColor + this.CloseArray + ChatColor.RESET;
    compactResult += this.OpenCloseArrayColor + this.CloseArray + ChatColor.RESET;
    if (compactResult.length < this.InlineThreshold) {
      return compactResult;
    }
    return result;
  }
  /**
   * Transforms an object into a truncated JSON representation.
   * @param value - The object to transform.
   * @param className - Class Name of the object.
   * @param indentLevel - The indentation level for pretty-printing.
   */
  stringifyTruncatedObject(value, className, ctx) {
    return (this.IncludeClassNames ? this.ClassColor + "" + this.ClassStyle + className + ChatColor.RESET + this.Space : "") + this.TruncatedObjectValue;
  }
  /**
   * Transforms an object into a JSON representation.
   * @param value - The object to transform.
   * @param className - Class Name of the object.
   * @param entries - Entries of the object to transform.
   * @param indentLevel - The indentation level for pretty-printing.
   */
  stringifyObject(value, className, entries, ctx) {
    const indentSpace = this.Indent.repeat(ctx.indentLevel);
    const prefix = this.IncludeClassNames && className !== "Object" ? this.ClassColor + "" + this.ClassStyle + className + ChatColor.RESET + this.Space : "";
    if (entries.length === 0) {
      return prefix + this.OpenCloseObjectColor + this.OpenObject + this.CloseObject + ChatColor.RESET;
    }
    let result = prefix + this.OpenCloseObjectColor + this.OpenObject + ChatColor.RESET + this.NewLine;
    let compactResult = prefix + this.OpenCloseObjectColor + this.OpenObject + ChatColor.RESET;
    entries.forEach(([key, val], index) => {
      const compactVal = this.stringifyValue(val, this.indent(ctx));
      result += indentSpace + this.Indent + this.KeyColor + this.KeyDelimiter + key + this.KeyDelimiter + ChatColor.RESET + this.KeyValueSeparator + this.Space + compactVal;
      result += index < entries.length - 1 ? this.Comma + this.NewLine : this.NewLine;
      compactResult += this.KeyColor + key + ChatColor.RESET + this.KeyValueSeparator + this.Space + compactVal;
      compactResult += index < entries.length - 1 ? this.Comma + this.Space : "";
    });
    result += indentSpace + this.OpenCloseObjectColor + this.CloseObject + ChatColor.RESET;
    compactResult += this.OpenCloseObjectColor + this.CloseObject + ChatColor.RESET;
    if (compactResult.length < this.InlineThreshold) {
      return compactResult;
    }
    return result;
  }
  shouldTruncateObject(value, className, ctx) {
    return !(className === "Object" || ctx.indentLevel <= this.MaxDepth || this.MaxDepth <= 0);
  }
  /**
   * Transforms a value of any type into a JSON representation. This function is not meant to be overridden.
   * @param value - The value to transform.
   * @param indentLevel - The indentation level for pretty-printing.
   */
  stringifyValue(value, ctx) {
    if (value === null)
      return this.stringifyNull();
    if (value === void 0)
      return this.stringifyUndefined();
    if (typeof value === "number")
      return this.stringifyNumber(value);
    if (typeof value === "string")
      return this.stringifyString(value);
    if (typeof value === "boolean")
      return this.stringifyBoolean(value);
    if (typeof value === "function")
      return this.stringifyFunction(value);
    if (this.isCycle(value, ctx)) {
      return this.stringifyCycle();
    }
    this.markCycle(value, ctx);
    if (Array.isArray(value)) {
      const result = this.stringifyArray(value, ctx.indentLevel ? this.indent(ctx) : ctx);
      this.clearCycle(value, ctx);
      return result;
    }
    if (typeof value === "object") {
      const name = value.constructor.name;
      if (!this.shouldTruncateObject(value, name, ctx)) {
        const keySet = /* @__PURE__ */ new Set();
        let prototype = Object.getPrototypeOf(value);
        let keys = Object.keys(prototype);
        while (keys.length > 0) {
          keys.forEach((key) => keySet.add(key));
          prototype = Object.getPrototypeOf(prototype);
          keys = Object.keys(prototype);
        }
        Object.keys(value).forEach((key) => keySet.add(key));
        keySet.delete("__cycleDetection__");
        const allKeys = [...keySet].sort();
        const entries = allKeys.map((key) => {
          try {
            return [key, value[key] ?? void 0];
          } catch (e) {
            return [key, void 0];
          }
        }).filter(([, val]) => typeof val !== "function" && val !== void 0);
        const result = this.stringifyObject(value, name, entries, ctx);
        this.clearCycle(value, ctx);
        return result;
      } else {
        const result = this.stringifyTruncatedObject(value, name, ctx);
        this.clearCycle(value, ctx);
        return result;
      }
    }
    this.clearCycle(value, ctx);
    return ChatColor.RESET + value.toString();
  }
  /**
   * Escapes a string for JSON.
   * @param str - The string to escape.
   */
  escapeString(str) {
    return str.replace(/\\/g, this.EscapeColor + "\\\\" + this.StringColor).replace(/"/g, this.EscapeColor + '\\"' + this.StringColor).replace(/\n/g, this.EscapeColor + "\\n" + this.StringColor).replace(/\r/g, this.EscapeColor + "\\r" + this.StringColor).replace(/\t/g, this.EscapeColor + "\\t" + this.StringColor);
  }
  markCycle(value, ctx) {
    ctx.visited.add(value);
  }
  isCycle(value, ctx) {
    return ctx.visited.has(value);
  }
  clearCycle(value, ctx) {
    ctx.visited.delete(value);
  }
  indent(ctx) {
    return { ...ctx, indentLevel: ctx.indentLevel + 1 };
  }
}, /**
 * The default ColorJSON instance
 */
__publicField(_a2, "DEFAULT", new _a2()), /**
 * A ColorJSON instance that does not colorize anything.
 */
__publicField(_a2, "PLAIN", _a2.createPlain()), _a2);
var sourceMapping = void 0;
try {
  sourceMapping = globalSourceMapping;
} catch (e) {
}
var _a3;
var LogLevel = (_a3 = class {
  /**
   * The constructor for each log level.
   *
   * @param {number} level - The numerical level for this logger.
   * @param {string} name - The string name for this logger.
   * @param {ChatColor} color - The color to use for this logger. Defaults to `ChatColor.RESET`.
   */
  constructor(level, name, color = ChatColor.RESET) {
    this.level = level;
    this.name = name;
    this.color = color;
  }
  /**
   * Return the logging level as a string.
   *
   * @returns {string} The string representation of the logging level.
   */
  toString() {
    return this.color + this.name.toUpperCase() + ChatColor.RESET;
  }
  /**
   * Parse a string to get the corresponding `LogLevel`.
   *
   * @param {string} str - The string to parse.
   * @returns {LogLevel} The corresponding `LogLevel`, or `undefined` if none was found.
   */
  static parse(str) {
    str = str.toLowerCase();
    for (const level of _a3.values) {
      if (level.name === str)
        return level;
    }
    const num = parseInt(str);
    if (!isNaN(num)) {
      for (const level of _a3.values) {
        if (level.level === num)
          return level;
      }
    }
    return void 0;
  }
}, __publicField(_a3, "All", new _a3(-2, "all")), __publicField(_a3, "Trace", new _a3(-2, "trace", ChatColor.DARK_AQUA)), __publicField(_a3, "Debug", new _a3(-1, "debug", ChatColor.AQUA)), __publicField(_a3, "Info", new _a3(0, "info", ChatColor.GREEN)), __publicField(_a3, "Warn", new _a3(1, "warn", ChatColor.GOLD)), __publicField(_a3, "Error", new _a3(2, "error", ChatColor.RED)), __publicField(_a3, "Fatal", new _a3(3, "fatal", ChatColor.DARK_RED)), __publicField(_a3, "Off", new _a3(100, "off")), /**
 * The list of all available log levels.
 */
__publicField(_a3, "values", [
  _a3.All,
  _a3.Trace,
  _a3.Debug,
  _a3.Info,
  _a3.Warn,
  _a3.Error,
  _a3.Fatal,
  _a3.Off
]), _a3);
function starMatch(pattern, str) {
  if (pattern === "*")
    return true;
  if (pattern.includes("*")) {
    if (pattern.startsWith("*")) {
      return str.endsWith(pattern.substring(1));
    }
    if (pattern.endsWith("*")) {
      return str.startsWith(pattern.substring(0, pattern.length - 1));
    }
    const regex = new RegExp(pattern.replace(/\*/g, ".*"));
    return regex.test(str);
  }
  return pattern === str;
}
var loggingSettings = {
  level: LogLevel.Info,
  filter: ["*"],
  outputTags: false,
  formatFunction: (level, logger, message, tags = void 0) => {
    const _tags = tags !== void 0 ? `\xA77${tags.map((tag) => `[${tag}]`).join("")}\xA7r` : "";
    return `[${level}][${ChatColor.MATERIAL_EMERALD}${logger.name}${ChatColor.RESET}]${_tags} ${message}`;
  },
  messagesJoinFunction: (messages) => {
    return messages.join(" ");
  },
  jsonFormatter: ColorJSON.DEFAULT,
  outputConfig: {
    [LogLevel.Trace.level]: [
      0,
      1
      /* ConsoleInfo */
    ],
    [LogLevel.Debug.level]: [
      0,
      1
      /* ConsoleInfo */
    ],
    [LogLevel.Info.level]: [
      0,
      1
      /* ConsoleInfo */
    ],
    [LogLevel.Warn.level]: [
      0,
      1,
      2
      /* ConsoleWarn */
    ],
    [LogLevel.Error.level]: [
      0,
      1,
      3
      /* ConsoleError */
    ],
    [LogLevel.Fatal.level]: [
      0,
      1,
      3
      /* ConsoleError */
    ]
  }
};
var _a4;
var Logger = (_a4 = class {
  /**
   * Construct a new Logger
   *
   * @param {string} name - The name of the Logger.
   * @param {string[]} tags - The tags for the logger as strings.
   */
  constructor(name, tags = []) {
    this.name = name;
    this.tags = tags;
  }
  /**
   *  Initialize logger class
   */
  static init() {
    LOGGING: {
      if (_a4.initialized)
        return;
      _a4.initialized = true;
      system2.afterEvents.scriptEventReceive.subscribe((ev) => {
        if (ev.id === "logging:level" || ev.id === "log:level") {
          if (!ev.message) {
            loggingSettings.level = LogLevel.Info;
            world2.sendMessage(
              `${ChatColor.AQUA}Logging level set to ${ChatColor.BOLD}${loggingSettings.level}`
            );
          } else {
            const level = LogLevel.parse(ev.message);
            if (level) {
              loggingSettings.level = level;
              world2.sendMessage(
                `${ChatColor.AQUA}Logging level set to ${ChatColor.BOLD}${loggingSettings.level}`
              );
            } else {
              world2.sendMessage(
                `${ChatColor.DARK_RED}Invalid logging level: ${ev.message}`
              );
            }
          }
        } else if (ev.id === "logging:filter" || ev.id === "log:filter") {
          if (!ev.message) {
            loggingSettings.filter = ["*"];
          } else {
            loggingSettings.filter = ev.message.split(",");
          }
          world2.sendMessage(
            `${ChatColor.AQUA}Logging filter set to ${ChatColor.BOLD}${loggingSettings.filter.join(", ")}`
          );
        }
      });
    }
  }
  /**
   * @param {LogLevel} level - The level to set.
   */
  static setLevel(level) {
    loggingSettings.level = level;
  }
  /**
   * Filter the loggers by the given tags. Tags can use the `*` wildcard.
   * @param {'*' | string[]} filter - The filter to set.
   */
  static setFilter(filter) {
    loggingSettings.filter = filter;
  }
  /**
   * Set the format function for the logger.
   * @param {function} func - The function to set.
   */
  static setFormatFunction(func) {
    loggingSettings.formatFunction = func;
  }
  /**
   * Set the function, that joins multiple messages into one for the logger.
   * @param {function} func - The function to set.
   */
  static setMessagesJoinFunction(func) {
    loggingSettings.messagesJoinFunction = func;
  }
  /**
   * Set the tag visibility for the logger. When true, tags will be printed in the log. Disabled by default.
   * @param visible
   */
  static setTagsOutputVisibility(visible) {
    loggingSettings.outputTags = visible;
  }
  /**
   * Set the JSON formatter for the logger.
   * @param {ColorJSON} formatter - The json formatter to set.
   */
  static setJsonFormatter(formatter) {
    loggingSettings.jsonFormatter = formatter;
  }
  /**
   * Get the output configuration for the logger.
   * @returns {OutputConfig} The output configuration.
   */
  static getOutputConfig() {
    return loggingSettings.outputConfig;
  }
  /**
   * Returns a new Logger.
   *
   * @param {string} name - The name of the Logger.
   * @param {string[]} tags - The tags for the Logger as strings.
   *
   * @returns {Logger} A new Logger.
   */
  static getLogger(name, ...tags) {
    LOGGING: {
      if (!_a4.initialized) {
        _a4.init();
      }
    }
    return new _a4(name, tags);
  }
  /**
   * Log messages with the level set.
   *
   * @param {LogLevel} level - The LogLevel to log the messages at.
   * @param {array} message - An array of the messages to log.
   */
  log(level, ...message) {
    LOGGING: {
      if (level.level < loggingSettings.level.level)
        return;
      if (loggingSettings.filter.length === 0 || this.tags.length === 0) {
        this.logRaw(level, ...message);
        return;
      }
      for (const filter of loggingSettings.filter) {
        if (filter.startsWith("!")) {
          if (starMatch(filter.substring(1), this.name) || this.tags.some((tag) => starMatch(filter.substring(1), tag))) {
            return;
          }
        }
        if (starMatch(filter, this.name) || this.tags.some((tag) => starMatch(filter, tag))) {
          this.logRaw(level, ...message);
          return;
        }
      }
    }
  }
  stringifyError(x) {
    let stack = x.stack ?? "";
    if (sourceMapping) {
      const stackLineRegex = /\(([^)]+\.js):(\d+)(?::(\d+))?\)/;
      stack = stack.split("\n").map((line) => {
        const match = stackLineRegex.exec(line);
        if (match) {
          const filePath = match[1];
          const lineNumber = parseInt(match[2], 10) - sourceMapping.metadata.offset;
          if (filePath.includes(sourceMapping.metadata.filePath)) {
            const mappingEntry = globalSourceMapping[lineNumber];
            if (mappingEntry) {
              const replacement = `(${mappingEntry.source}:${mappingEntry.originalLine})`;
              return line.replace(stackLineRegex, replacement);
            }
          }
        }
        return line;
      }).join("\n");
    }
    return `${ChatColor.DARK_RED}${ChatColor.BOLD}${x.message}
${ChatColor.RESET}${ChatColor.GRAY}${ChatColor.ITALIC}${stack}${ChatColor.RESET}`;
  }
  /**
   * Internal function to log messages with the level set, that bypasses the filters.
   *
   * @param {LogLevel} level - The LogLevel to log the messages at.
   * @param {array} message - An array of the messages to log.
   */
  logRaw(level, ...message) {
    LOGGING: {
      const msgs = message.map((x) => {
        if (x === void 0) {
          return ChatColor.GOLD + "undefined" + ChatColor.RESET;
        }
        if (x === null) {
          return ChatColor.GOLD + "null" + ChatColor.RESET;
        }
        if (x && x instanceof Error) {
          return this.stringifyError(x);
        }
        if (typeof x === "object" || Array.isArray(x)) {
          return loggingSettings.jsonFormatter.stringify(x) + ChatColor.RESET;
        }
        return x.toString() + ChatColor.RESET;
      });
      const formatted = loggingSettings.formatFunction(
        level,
        this,
        loggingSettings.messagesJoinFunction(msgs),
        loggingSettings.outputTags ? this.tags : void 0
      );
      const outputs = loggingSettings.outputConfig[level.level] || [
        0,
        1
        /* ConsoleInfo */
      ];
      if (outputs.includes(
        0
        /* Chat */
      )) {
        try {
          world2.sendMessage(formatted);
        } catch (_) {
          system2.run(() => {
            world2.sendMessage(formatted);
          });
        }
      }
      if (outputs.includes(
        1
        /* ConsoleInfo */
      )) {
        if (console.originalLog) {
          console.originalLog(ChatColor.stripColor(formatted));
        } else {
          console.log(ChatColor.stripColor(formatted));
        }
      }
      if (outputs.includes(
        2
        /* ConsoleWarn */
      )) {
        console.warn(formatted);
      }
      if (outputs.includes(
        3
        /* ConsoleError */
      )) {
        console.error(formatted);
      }
    }
  }
  /**
   * Logs a trace message.
   *
   * @param {...unknown} message - The message(s) to be logged.
   */
  trace(...message) {
    LOGGING:
      this.log(LogLevel.Trace, ...message);
  }
  /**
   * Logs debug message.
   *
   * @param {...unknown[]} message - The message(s) to be logged.
   */
  debug(...message) {
    LOGGING:
      this.log(LogLevel.Debug, ...message);
  }
  /**
   * Logs an informational message.
   *
   * @param {...unknown[]} message - The message(s) to be logged.
   */
  info(...message) {
    LOGGING:
      this.log(LogLevel.Info, ...message);
  }
  /**
   * Logs a warning message.
   *
   * @param {...unknown[]} message - The warning message or messages to be logged.
   */
  warn(...message) {
    LOGGING:
      this.log(LogLevel.Warn, ...message);
  }
  /**
   * Logs an error message.
   *
   * @param {...unknown[]} message - The error message(s) to log.
   */
  error(...message) {
    LOGGING:
      this.log(LogLevel.Error, ...message);
  }
  /**
   * Logs a fatal error.
   *
   * @param {unknown[]} message - The error message to log.
   */
  fatal(...message) {
    LOGGING:
      this.log(LogLevel.Fatal, ...message);
  }
}, __publicField(_a4, "initialized", false), _a4);
var _a5;
var Vec3 = (_a5 = class {
  constructor(x, y, z) {
    __publicField(this, "x");
    __publicField(this, "y");
    __publicField(this, "z");
    if (x === Direction.Down) {
      this.x = 0;
      this.y = -1;
      this.z = 0;
    } else if (x === Direction.Up) {
      this.x = 0;
      this.y = 1;
      this.z = 0;
    } else if (x === Direction.North) {
      this.x = 0;
      this.y = 0;
      this.z = -1;
    } else if (x === Direction.South) {
      this.x = 0;
      this.y = 0;
      this.z = 1;
    } else if (x === Direction.East) {
      this.x = 1;
      this.y = 0;
      this.z = 0;
    } else if (x === Direction.West) {
      this.x = -1;
      this.y = 0;
      this.z = 0;
    } else if (typeof x === "number") {
      this.x = x;
      this.y = y;
      this.z = z;
    } else if (Array.isArray(x)) {
      this.x = x[0];
      this.y = x[1];
      this.z = x[2];
    } else if (x instanceof _a5) {
      this.x = x.x;
      this.y = x.y;
      this.z = x.z;
    } else {
      if (!x || !x.x && x.x !== 0 || !x.y && x.y !== 0 || !x.z && x.z !== 0) {
        _a5.log.error(new Error("Invalid vector"), x);
        throw new Error("Invalid vector");
      }
      this.x = x.x;
      this.y = x.y;
      this.z = x.z;
    }
  }
  static from(x, y, z) {
    if (x instanceof _a5)
      return x;
    if (typeof x === "number" && y !== void 0 && z !== void 0) {
      return new _a5(x, y, z);
    }
    if (Array.isArray(x)) {
      return new _a5(x);
    }
    if (x === Direction.Down)
      return _a5.Down;
    if (x === Direction.Up)
      return _a5.Up;
    if (x === Direction.North)
      return _a5.North;
    if (x === Direction.South)
      return _a5.South;
    if (x === Direction.East)
      return _a5.East;
    if (x === Direction.West)
      return _a5.West;
    if (!x || !x.x && x.x !== 0 || !x.y && x.y !== 0 || !x.z && x.z !== 0) {
      _a5.log.error(new Error("Invalid arguments"), x, y, z);
      throw new Error("Invalid arguments");
    }
    return new _a5(
      x.x,
      x.y,
      x.z
    );
  }
  static _from(x, y, z) {
    if (x instanceof _a5)
      return x;
    if (typeof x === "number" && y !== void 0 && z !== void 0) {
      return new _a5(x, y, z);
    }
    if (Array.isArray(x)) {
      return new _a5(x);
    }
    if (x === Direction.Down)
      return _a5.Down;
    if (x === Direction.Up)
      return _a5.Up;
    if (x === Direction.North)
      return _a5.North;
    if (x === Direction.South)
      return _a5.South;
    if (x === Direction.East)
      return _a5.East;
    if (x === Direction.West)
      return _a5.West;
    if (!x || !x.x && x.x !== 0 || !x.y && x.y !== 0 || !x.z && x.z !== 0) {
      _a5.log.error(new Error("Invalid arguments"), x, y, z);
      throw new Error("Invalid arguments");
    }
    return new _a5(
      x.x,
      x.y,
      x.z
    );
  }
  /**
   * Creates a copy of the current vector.
   *
   * @returns A new vector with the same values as the current vector.
   */
  copy() {
    return new _a5(this.x, this.y, this.z);
  }
  static fromYawPitch(yawOrRotation, pitch) {
    let yaw;
    if (typeof yawOrRotation === "number") {
      yaw = yawOrRotation;
      pitch = pitch;
    } else {
      yaw = yawOrRotation.y;
      pitch = yawOrRotation.x;
    }
    const psi = yaw * (Math.PI / 180);
    const theta = pitch * (Math.PI / 180);
    const x = Math.cos(theta) * Math.sin(psi);
    const y = Math.sin(theta);
    const z = Math.cos(theta) * Math.cos(psi);
    return new _a5(x, y, z);
  }
  static fromRotation(yawOrRotation, pitch) {
    let yaw;
    if (typeof yawOrRotation === "number") {
      yaw = yawOrRotation;
      pitch = pitch;
    } else {
      yaw = yawOrRotation.y;
      pitch = yawOrRotation.x;
    }
    const psi = yaw * (Math.PI / 180);
    const theta = pitch * (Math.PI / 180);
    const x = -Math.cos(theta) * Math.sin(psi);
    const y = -Math.sin(theta);
    const z = Math.cos(theta) * Math.cos(psi);
    return new _a5(x, y, z);
  }
  /**
   * Converts the normal vector to yaw and pitch values.
   *
   * @returns A Vector2 containing the yaw and pitch values.
   * @deprecated Use toRotation() instead. This method returns inverted values and will be removed in the future.
   */
  toYawPitch() {
    if (this.isZero()) {
      _a5.log.error(
        new Error("Cannot convert zero-length vector to direction")
      );
      throw new Error("Cannot convert zero-length vector to direction");
    }
    const direction = this.normalize();
    const yaw = Math.atan2(direction.x, direction.z) * (180 / Math.PI);
    const pitch = Math.asin(direction.y) * (180 / Math.PI);
    return {
      x: pitch,
      y: yaw
    };
  }
  /**
   * Converts the normal vector to yaw and pitch values.
   *
   * @returns A Vector2 containing the yaw and pitch values.
   */
  toRotation() {
    if (this.isZero()) {
      _a5.log.error(
        new Error("Cannot convert zero-length vector to direction")
      );
      throw new Error("Cannot convert zero-length vector to direction");
    }
    const direction = this.normalize();
    const yaw = -Math.atan2(direction.x, direction.z) * (180 / Math.PI);
    const pitch = Math.asin(-direction.y) * (180 / Math.PI);
    return {
      x: pitch,
      y: yaw
    };
  }
  add(x, y, z) {
    const v = _a5._from(x, y, z);
    return _a5.from(v.x + this.x, v.y + this.y, v.z + this.z);
  }
  subtract(x, y, z) {
    const v = _a5._from(x, y, z);
    return _a5.from(this.x - v.x, this.y - v.y, this.z - v.z);
  }
  multiply(x, y, z) {
    if (typeof x === "number" && y === void 0 && z === void 0) {
      return _a5.from(this.x * x, this.y * x, this.z * x);
    }
    const v = _a5._from(x, y, z);
    return _a5.from(v.x * this.x, v.y * this.y, v.z * this.z);
  }
  /**
   * Scales the current vector by a scalar.
   *
   * @param scalar - The scalar to scale the vector by.
   * @returns The updated vector after scaling.
   */
  scale(scalar) {
    return _a5.from(this.x * scalar, this.y * scalar, this.z * scalar);
  }
  divide(x, y, z) {
    if (typeof x === "number" && y === void 0 && z === void 0) {
      if (x === 0)
        throw new Error("Cannot divide by zero");
      return _a5.from(this.x / x, this.y / x, this.z / x);
    }
    const v = _a5._from(x, y, z);
    if (v.x === 0 || v.y === 0 || v.z === 0)
      throw new Error("Cannot divide by zero");
    return _a5.from(this.x / v.x, this.y / v.y, this.z / v.z);
  }
  /**
   * Normalizes the vector to have a length (magnitude) of 1.
   * Normalized vectors are often used as a direction vectors.
   *
   * @returns The normalized vector.
   */
  normalize() {
    if (this.isZero()) {
      _a5.log.error(new Error("Cannot normalize zero-length vector"));
      throw new Error("Cannot normalize zero-length vector");
    }
    const len = this.length();
    return _a5.from(this.x / len, this.y / len, this.z / len);
  }
  /**
   * Computes the length (magnitude) of the vector.
   *
   * @returns The length of the vector.
   */
  length() {
    return Math.hypot(this.x, this.y, this.z);
  }
  /**
   * Computes the squared length of the vector.
   * This is faster than computing the actual length and can be useful for comparison purposes.
   *
   * @returns The squared length of the vector.
   */
  lengthSquared() {
    return this.x * this.x + this.y * this.y + this.z * this.z;
  }
  cross(x, y, z) {
    const v = _a5._from(x, y, z);
    return _a5.from(
      this.y * v.z - this.z * v.y,
      this.z * v.x - this.x * v.z,
      this.x * v.y - this.y * v.x
    );
  }
  distance(x, y, z) {
    const v = _a5._from(x, y, z);
    return this.subtract(v).length();
  }
  distanceSquared(x, y, z) {
    const v = _a5._from(x, y, z);
    return this.subtract(v).lengthSquared();
  }
  /**
   * Computes the linear interpolation between the current vector and another vector, when t is in the range [0, 1].
   * Computes the extrapolation when t is outside this range.
   *
   * @param v - The other vector.
   * @param t - The interpolation factor.
   * @returns A new vector after performing the lerp operation.
   */
  lerp(v, t) {
    if (!v || !t)
      return _a5.from(this);
    if (t === 1)
      return _a5.from(v);
    if (t === 0)
      return _a5.from(this);
    return _a5.from(
      this.x + (v.x - this.x) * t,
      this.y + (v.y - this.y) * t,
      this.z + (v.z - this.z) * t
    );
  }
  /**
   * Computes the spherical linear interpolation between the current vector and another vector, when t is in the range [0, 1].
   * Computes the extrapolation when t is outside this range.
   *
   * @param v - The other vector.
   * @param t - The interpolation factor.
   * @returns A new vector after performing the slerp operation.
   */
  slerp(v, t) {
    if (!v || !t)
      return _a5.from(this);
    if (t === 1)
      return _a5.from(v);
    if (t === 0)
      return _a5.from(this);
    const dot = this.dot(v);
    const theta = Math.acos(dot) * t;
    const relative = _a5.from(v).subtract(this.multiply(dot)).normalize();
    return this.multiply(Math.cos(theta)).add(
      relative.multiply(Math.sin(theta))
    );
  }
  dot(x, y, z) {
    const v = _a5._from(x, y, z);
    return this.x * v.x + this.y * v.y + this.z * v.z;
  }
  angleBetween(x, y, z) {
    const v = _a5._from(x, y, z);
    const dotProduct = this.dot(v);
    const lenSq1 = this.lengthSquared();
    if (lenSq1 === 0) {
      return 0;
    }
    const lenSq2 = v.lengthSquared();
    if (lenSq2 === 0) {
      return 0;
    }
    const denom = Math.sqrt(lenSq1 * lenSq2);
    const cosAngle = Math.min(1, Math.max(-1, dotProduct / denom));
    return Math.acos(cosAngle);
  }
  projectOnto(x, y, z) {
    const v = _a5._from(x, y, z);
    if (v.isZero()) {
      return _a5.Zero;
    }
    const denom = v.dot(v);
    if (denom === 0) {
      return _a5.Zero;
    }
    const scale = this.dot(v) / denom;
    return _a5.from(v.x * scale, v.y * scale, v.z * scale);
  }
  reflect(x, y, z) {
    const normal = _a5._from(x, y, z);
    const proj = this.projectOnto(normal);
    return this.subtract(proj.multiply(2));
  }
  /**
   * Rotates the current normalized vector by a given angle around a given axis.
   *
   * @param axis - The axis of rotation.
   * @param angle - The angle of rotation in degrees.
   * @returns The rotated vector.
   */
  rotate(axis, angle) {
    const halfAngle = angle * Math.PI / 180 / 2;
    const w = Math.cos(halfAngle);
    const x = axis.x * Math.sin(halfAngle);
    const y = axis.y * Math.sin(halfAngle);
    const z = axis.z * Math.sin(halfAngle);
    const v = this;
    const qv_x = w * w * v.x + 2 * y * w * v.z - 2 * z * w * v.y + x * x * v.x + 2 * y * x * v.y + 2 * z * x * v.z - z * z * v.x - y * y * v.x;
    const qv_y = 2 * x * y * v.x + y * y * v.y + 2 * z * y * v.z + 2 * w * z * v.x - z * z * v.y + w * w * v.y - 2 * x * w * v.z - x * x * v.y;
    const qv_z = 2 * x * z * v.x + 2 * y * z * v.y + z * z * v.z - 2 * w * y * v.x - y * y * v.z + 2 * w * x * v.y - x * x * v.z + w * w * v.z;
    return new _a5(qv_x, qv_y, qv_z);
  }
  /**
   * Updates the X, Y, and Z components of the vector.
   *
   * @param x - The function to use to update the X value.
   * @param y - The function to use to update the Y value.
   * @param z - The function to use to update the Z value.
   * @returns The updated vector with the new values.
   */
  update(x, y, z) {
    if (!x) {
      x = (value) => value;
    }
    if (!y) {
      y = (value) => value;
    }
    if (!z) {
      z = (value) => value;
    }
    return new _a5(x(this.x), y(this.y), z(this.z));
  }
  setX(value) {
    if (typeof value === "number") {
      return new _a5(value, this.y, this.z);
    }
    return new _a5(value(this.x), this.y, this.z);
  }
  setY(value) {
    if (typeof value === "number") {
      return new _a5(this.x, value, this.z);
    }
    return new _a5(this.x, value(this.y), this.z);
  }
  setZ(value) {
    if (typeof value === "number") {
      return new _a5(this.x, this.y, value);
    }
    return new _a5(this.x, this.y, value(this.z));
  }
  /**
   * Calculates the shortest distance between a point (represented by this Vector3 instance) and a line segment.
   *
   * This method finds the perpendicular projection of the point onto the line defined by the segment. If this
   * projection lies outside the line segment, then the method calculates the distance from the point to the
   * nearest segment endpoint.
   *
   * @param start - The starting point of the line segment.
   * @param end - The ending point of the line segment.
   * @returns The shortest distance between the point and the line segment.
   */
  distanceToLineSegment(start, end) {
    const lineDirection = _a5.from(end).subtract(start);
    if (lineDirection.lengthSquared() === 0) {
      return this.subtract(start).length();
    }
    const t = Math.max(
      0,
      Math.min(
        1,
        this.subtract(start).dot(lineDirection) / lineDirection.dot(lineDirection)
      )
    );
    const projection = _a5.from(start).add(lineDirection.multiply(t));
    return this.subtract(projection).length();
  }
  /**
   * Floors the X, Y, and Z components of the vector.
   * @returns A new vector with the floored components.
   */
  floor() {
    return this.update(Math.floor, Math.floor, Math.floor);
  }
  /**
   * Floors the X component of the vector.
   * @returns A new vector with the floored X component.
   */
  floorX() {
    return this.setX(Math.floor);
  }
  /**
   * Floors the Y component of the vector.
   * @returns A new vector with the floored Y component.
   */
  floorY() {
    return this.setY(Math.floor);
  }
  /**
   * Floors the Z component of the vector.
   * @returns A new vector with the floored Z component.
   */
  floorZ() {
    return this.setZ(Math.floor);
  }
  /**
   * Ceils the X, Y, and Z components of the vector.
   * @returns A new vector with the ceiled components.
   */
  ceil() {
    return new _a5(Math.ceil(this.x), Math.ceil(this.y), Math.ceil(this.z));
  }
  /**
   * Ceils the X component of the vector.
   * @returns A new vector with the ceiled X component.
   */
  ceilX() {
    return this.setX(Math.ceil);
  }
  /**
   * Ceils the Y component of the vector.
   * @returns A new vector with the ceiled Y component.
   */
  ceilY() {
    return this.setY(Math.ceil);
  }
  /**
   * Ceils the Z component of the vector.
   * @returns A new vector with the ceiled Z component.
   */
  ceilZ() {
    return this.setZ(Math.ceil);
  }
  /**
   * Rounds the X, Y, and Z components of the vector.
   * @returns A new vector with the rounded components.
   */
  round() {
    return this.update(Math.round, Math.round, Math.round);
  }
  /**
   * Rounds the X component of the vector.
   * @returns A new vector with the rounded X component.
   */
  roundX() {
    return this.setX(Math.round);
  }
  /**
   * Rounds the Y component of the vector.
   * @returns A new vector with the rounded Y component.
   */
  roundY() {
    return this.setY(Math.round);
  }
  /**
   * Rounds the Z component of the vector.
   * @returns A new vector with the rounded Z component.
   */
  roundZ() {
    return this.setZ(Math.round);
  }
  /**
   * Returns a new vector offset from the current vector up by 1 block.
   * @returns A new vector offset from the current vector up by 1 block.
   */
  up() {
    return this.add(_a5.Up);
  }
  /**
   * Returns a new vector offset from the current vector down by 1 block.
   * @returns A new vector offset from the current vector down by 1 block.
   */
  down() {
    return this.add(_a5.Down);
  }
  /**
   * Returns a new vector offset from the current vector north by 1 block.
   * @returns A new vector offset from the current vector north by 1 block.
   */
  north() {
    return this.add(_a5.North);
  }
  /**
   * Returns a new vector offset from the current vector south by 1 block.
   * @returns A new vector offset from the current vector south by 1 block.
   */
  south() {
    return this.add(_a5.South);
  }
  /**
   * Returns a new vector offset from the current vector east by 1 block.
   * @returns A new vector offset from the current vector east by 1 block.
   */
  east() {
    return this.add(_a5.East);
  }
  /**
   * Returns a new vector offset from the current vector west by 1 block.
   * @returns A new vector offset from the current vector west by 1 block.
   */
  west() {
    return this.add(_a5.West);
  }
  /**
   * Checks if the current vector is equal to the zero vector.
   * @returns true if the vector is equal to the zero vector, else returns false.
   */
  isZero() {
    return this.x === 0 && this.y === 0 && this.z === 0;
  }
  /**
   * Converts the vector to an array containing the X, Y, and Z components of the vector.
   * @returns An array containing the X, Y, and Z components of the vector.
   */
  toArray() {
    return [this.x, this.y, this.z];
  }
  /**
   * Converts the vector to a direction.
   * If the vector is not a unit vector, then it will be normalized and rounded to the nearest direction.
   */
  toDirection() {
    if (this.isZero()) {
      _a5.log.error(
        new Error("Cannot convert zero-length vector to direction")
      );
      throw new Error("Cannot convert zero-length vector to direction");
    }
    const normalized = this.normalize();
    const maxValue = Math.max(
      Math.abs(normalized.x),
      Math.abs(normalized.y),
      Math.abs(normalized.z)
    );
    if (maxValue === normalized.x)
      return Direction.East;
    if (maxValue === -normalized.x)
      return Direction.West;
    if (maxValue === normalized.y)
      return Direction.Up;
    if (maxValue === -normalized.y)
      return Direction.Down;
    if (maxValue === normalized.z)
      return Direction.South;
    if (maxValue === -normalized.z)
      return Direction.North;
    _a5.log.error(new Error("Cannot convert vector to direction"), this);
    throw new Error("Cannot convert vector to direction");
  }
  /**
   * Returns a new vector with the X, Y, and Z components rounded to the nearest block location.
   */
  toBlockLocation() {
    return _a5.from(
      (this.x << 0) - (this.x < 0 && this.x !== this.x << 0 ? 1 : 0),
      (this.y << 0) - (this.y < 0 && this.y !== this.y << 0 ? 1 : 0),
      (this.z << 0) - (this.z < 0 && this.z !== this.z << 0 ? 1 : 0)
    );
  }
  almostEqual(x, y, z, delta) {
    try {
      let other;
      if (typeof x !== "number" && z === void 0) {
        other = _a5._from(x, void 0, void 0);
        delta = y;
      } else {
        other = _a5._from(x, y, z);
      }
      return Math.abs(this.x - other.x) <= delta && Math.abs(this.y - other.y) <= delta && Math.abs(this.z - other.z) <= delta;
    } catch (e) {
      return false;
    }
  }
  equals(x, y, z) {
    try {
      const other = _a5._from(x, y, z);
      return this.x === other.x && this.y === other.y && this.z === other.z;
    } catch (e) {
      return false;
    }
  }
  /**
   * Converts the vector to a string representation.
   *
   * @param format - The format of the string representation. Defaults to "long".
   * @param separator - The separator to use between components. Defaults to ", ".
   * @returns The string representation of the vector.
   * @remarks
   * The "long" format is "Vec3(x, y, z)".
   * The "short" format is "x, y, z".
   */
  toString(format = "long", separator = ", ") {
    const result = `${this.x + separator + this.y + separator + this.z}`;
    return format === "long" ? `Vec3(${result})` : result;
  }
  /**
   * Parses a string representation of a vector.
   *
   * @param str - The string representation of the vector.
   * @param format - The format of the string representation. Defaults to "long".
   * @param separator - The separator to use between components. Defaults to ", ".
   * @returns The vector parsed from the string.
   * @throws {Error} If the string format is invalid.
   */
  static fromString(str, format = "long", separator = ", ") {
    if (format === "long") {
      const match = str.match(/^Vec3\((.*)\)$/);
      if (!match) {
        throw new Error("Invalid string format");
      }
      const components = match[1].split(separator);
      if (components.length !== 3) {
        throw new Error("Invalid string format");
      }
      return _a5.from(Number(components[0]), Number(components[1]), Number(components[2]));
    } else {
      const components = str.split(separator);
      if (components.length !== 3) {
        throw new Error("Invalid string format");
      }
      return _a5.from(Number(components[0]), Number(components[1]), Number(components[2]));
    }
  }
}, __publicField(_a5, "log", Logger.getLogger(
  "vec3",
  "vec3",
  "bedrock-boost"
)), /**
 * Zero vector
 */
__publicField(_a5, "Zero", new _a5(0, 0, 0)), /**
 * Down vector, negative towards Y
 */
__publicField(_a5, "Down", new _a5(Direction.Down)), /**
 * Up vector, positive towards Y
 */
__publicField(_a5, "Up", new _a5(Direction.Up)), /**
 * North vector, negative towards Z
 */
__publicField(_a5, "North", new _a5(Direction.North)), /**
 * South vector, positive towards Z
 */
__publicField(_a5, "South", new _a5(Direction.South)), /**
 * East vector, positive towards X
 */
__publicField(_a5, "East", new _a5(Direction.East)), /**
 * West vector, negative towards X
 */
__publicField(_a5, "West", new _a5(Direction.West)), _a5);
var _a6;
var Timings = (_a6 = class {
  /**
   * Begin measuring the time it takes to perform an operation.
   * @remarks
   * If another operation is already being measured, the measurement will be ended.
   * 
   * @param operation The name of the operation.
   */
  static begin(operation) {
    this.end();
    this.lastTime = (/* @__PURE__ */ new Date()).getTime();
    this.lastOperation = operation;
  }
  /**
   * End measuring the time it takes to perform an operation and log the result.
   * @remarks
   * If no operation is being measured, this method will do nothing.
   */
  static end() {
    const time = (/* @__PURE__ */ new Date()).getTime();
    if (this.lastTime > 0) {
      _a6.log.debug(`Operation ${this.lastOperation} took ${time - this.lastTime}ms`);
    }
    this.lastTime = -1;
  }
}, __publicField(_a6, "log", Logger.getLogger("Timings", "timings")), __publicField(_a6, "lastTime", -1), __publicField(_a6, "lastOperation", ""), _a6);
function isValid(entity) {
  const f = Object.getPrototypeOf(entity).isValid;
  if (typeof f === "function") {
    return f.call(entity);
  }
  return entity.isValid;
}
var log = Logger.getLogger("jobUtils", "bedrock-boost", "jobUtils");
var _a7;
var PulseScheduler = (_a7 = class {
  /**
   * Creates a new PulseScheduler instance.
   * @param period The period of the scheduler.
   */
  constructor(processor, period) {
    __publicField(this, "items", []);
    __publicField(this, "period");
    __publicField(this, "currentTick", 0);
    __publicField(this, "runId");
    __publicField(this, "nextIndex", 0);
    __publicField(this, "executionSchedule", []);
    __publicField(this, "processor");
    if (period <= 0) {
      throw new Error("Period must be a positive integer.");
    }
    if (!processor || typeof processor !== "function") {
      throw new Error("Processor function must be defined.");
    }
    this.period = period;
    this.processor = processor;
  }
  /**
   * Adds an item to the schedule.
   * @param item The item to be added.
   * @deprecated Use `push` instead.
   */
  add(item) {
    this.push(item);
  }
  /**
    * Adds multiple items to the schedule.
    * 
    * @param items - The items to be added.
    * @deprecated Use `push` instead.
    */
  addAll(items) {
    this.push(...items);
  }
  /**
   * Removes an item from the schedule at the specified index.
   * @param index - The index of the item to remove.
   */
  remove(index) {
    if (index >= 0 && index < this.items.length) {
      this.items.splice(index, 1);
      if (index < this.nextIndex) {
        this.nextIndex--;
      }
      this.recalculateExecutionSchedule();
    }
  }
  /**
   * Removes items from the schedule that satisfy the given predicate.
   * 
   * @param predicate - The predicate function used to determine if an item should be removed.
   */
  removeIf(predicate) {
    for (let i = this.items.length - 1; i >= 0; i--) {
      if (predicate(this.items[i])) {
        this.remove(i);
      }
    }
  }
  /**
   * Returns a list of the items in the schedule.
   */
  getItems() {
    return this.items;
  }
  /**
   * Starts the schedule.
   */
  start() {
    this.stop();
    this.currentTick = 0;
    this.nextIndex = 0;
    this.runId = system4.runInterval(() => this.tick(), 1);
  }
  /**
   * Stops the schedule.
   */
  stop() {
    if (this.runId !== void 0) {
      system4.clearRun(this.runId);
      this.runId = void 0;
    }
  }
  recalculateExecutionSchedule() {
    const totalExecutions = this.items.length;
    this.executionSchedule = new Array(this.period).fill(0);
    if (totalExecutions === 0) {
      return;
    }
    const interval = this.period / totalExecutions;
    for (let i = 0; i < totalExecutions; i++) {
      this.executionSchedule[Math.round(interval * i) % this.period]++;
    }
  }
  tick() {
    if (this.items.length === 0) {
      _a7.log.trace("No items to process.");
      return;
    }
    const scheduledExecutions = this.executionSchedule[this.currentTick];
    if (scheduledExecutions === 0) {
      _a7.log.trace("No items to process this tick.");
      this.currentTick = (this.currentTick + 1) % this.period;
      if (this.currentTick === 0) {
        this.nextIndex = 0;
      }
      return;
    }
    let executed = 0;
    for (; this.nextIndex < this.items.length && executed < scheduledExecutions; this.nextIndex++) {
      try {
        this.processor(this.items[this.nextIndex]);
      } catch (e) {
        _a7.log.error("Error processing item", e);
      }
      executed++;
    }
    this.currentTick = (this.currentTick + 1) % this.period;
    if (this.currentTick === 0) {
      this.nextIndex = 0;
    }
  }
  push(...items) {
    this.items.push(...items);
    this.recalculateExecutionSchedule();
    return this.items.length;
  }
  pop() {
    const item = this.items.pop();
    this.recalculateExecutionSchedule();
    return item;
  }
  shift() {
    const item = this.items.shift();
    this.recalculateExecutionSchedule();
    return item;
  }
  unshift(...items) {
    this.items.unshift(...items);
    this.recalculateExecutionSchedule();
    return this.items.length;
  }
  splice(start, deleteCount = 0, ...items) {
    const removed = this.items.splice(start, deleteCount, ...items);
    this.recalculateExecutionSchedule();
    return removed;
  }
}, __publicField(_a7, "log", Logger.getLogger("PulseScheduler", "bedrock-boost", "pulse-scheduler")), _a7);
var _a8;
var EntityPulseScheduler = (_a8 = class extends PulseScheduler {
  /**
   * Creates a new EntityPulseScheduler instance.
   * @param period The period of the scheduler.
   * @param queryOptions The query options to use when querying for entities.
   */
  constructor(processor, period, queryOptions) {
    super((t) => {
      if (isValid(t)) {
        processor(t);
      } else {
        this.removeIf((entity) => !isValid(entity));
      }
    }, period);
    this.queryOptions = queryOptions;
    this.push(
      ...world4.getDimension("minecraft:overworld").getEntities(this.queryOptions)
    );
    this.push(
      ...world4.getDimension("minecraft:nether").getEntities(this.queryOptions)
    );
    this.push(
      ...world4.getDimension("minecraft:the_end").getEntities(this.queryOptions)
    );
  }
  compareEntities(a, b) {
    return a.id === b.id;
  }
  start() {
    world4.afterEvents.entityLoad.subscribe((event) => {
      this.addIfMatchesWithRetry(event.entity);
    });
    world4.afterEvents.entitySpawn.subscribe((event) => {
      this.addIfMatchesWithRetry(event.entity);
    });
    world4.afterEvents.entityRemove.subscribe((event) => {
      this.removeIf(
        (entity) => !isValid(entity) || entity.id === event.removedEntityId
      );
    });
    super.start();
  }
  /**
   * Adds an entity to the scheduler if it matches the query options. In case the entity is not valid, it will retry a tick later.
   * @param entity The entity to add.
   */
  addIfMatchesWithRetry(entity) {
    try {
      if (!entity) {
        return;
      }
      if (!isValid(entity)) {
        system5.runInterval(() => {
          if (isValid(entity) && entity.matches(this.queryOptions)) {
            this.push(entity);
          }
        }, 1);
      } else if (entity.matches(this.queryOptions)) {
        this.push(entity);
      }
    } catch (e) {
      _a8.logger.debug(
        "Failed to push entity to scheduler.",
        e
      );
    }
  }
  push(...items) {
    const filtered = items.filter(
      (item) => isValid(item) && !this.items.some(
        (existingItem) => this.compareEntities(existingItem, item)
      )
    );
    return super.push(...filtered);
  }
  unshift(...items) {
    const filtered = items.filter(
      (item) => isValid(item) && !this.items.some(
        (existingItem) => this.compareEntities(existingItem, item)
      )
    );
    return super.unshift(...filtered);
  }
  splice(start, deleteCount, ...items) {
    if (deleteCount === void 0) {
      return super.splice(start);
    }
    const filtered = items.filter(
      (item) => !this.items.some(
        (existingItem) => this.compareEntities(existingItem, item)
      )
    );
    return super.splice(start, deleteCount, ...filtered);
  }
}, __publicField(_a8, "logger", Logger.getLogger(
  "EntityPulseScheduler",
  "bedrock-boost",
  "entity-pulse-scheduler"
)), _a8);
var _a9;
var PlayerPulseScheduler = (_a9 = class extends PulseScheduler {
  /**
   * Creates a new PlayerPulseScheduler instance.
   * @param period The period of the scheduler.
   */
  constructor(processor, period) {
    super((t) => {
      if (isValid(t)) {
        processor(t);
      } else {
        this.removeIf((entity) => !isValid(entity));
      }
    }, period);
    this.push(...world5.getAllPlayers());
  }
  compareEntities(a, b) {
    return a.id === b.id;
  }
  start() {
    world5.afterEvents.playerJoin.subscribe((event) => {
      let attempts = 0;
      const pushPlayer = () => {
        attempts++;
        if (attempts > 10) {
          _a9.logger.debug("Failed to push player to scheduler after 10 attempts.");
          return;
        }
        try {
          const player = world5.getEntity(event.playerId);
          if (player === void 0) {
            system6.runTimeout(pushPlayer, 1);
          }
          if (player instanceof Player2) {
            this.push(player);
          }
        } catch (e) {
          _a9.logger.debug("Failed to push player to scheduler.", e);
          system6.runTimeout(pushPlayer, 1);
        }
      };
      pushPlayer();
    });
    world5.afterEvents.playerLeave.subscribe((event) => {
      this.removeIf((entity) => !isValid(entity) || entity.id === event.playerId);
    });
    super.start();
  }
  push(...items) {
    const filtered = items.filter((item) => isValid(item) && !this.items.some((existingItem) => this.compareEntities(existingItem, item)));
    return super.push(...filtered);
  }
  unshift(...items) {
    const filtered = items.filter((item) => isValid(item) && !this.items.some((existingItem) => this.compareEntities(existingItem, item)));
    return super.unshift(...filtered);
  }
  splice(start, deleteCount, ...items) {
    if (deleteCount === void 0) {
      return super.splice(start);
    }
    const filtered = items.filter((item) => !this.items.some((existingItem) => this.compareEntities(existingItem, item)));
    return super.splice(start, deleteCount, ...filtered);
  }
}, __publicField(_a9, "logger", Logger.getLogger("PlayerPulseScheduler", "bedrock-boost", "player-pulse-scheduler")), _a9);
var _a10;
var DirectionUtils = (_a10 = class {
}, /**
 * The opposite directions of the given directions.
 */
__publicField(_a10, "Opposites", {
  [Direction2.Down]: Direction2.Up,
  [Direction2.Up]: Direction2.Down,
  [Direction2.North]: Direction2.South,
  [Direction2.South]: Direction2.North,
  [Direction2.East]: Direction2.West,
  [Direction2.West]: Direction2.East
}), /**
 * The positive perpendicular directions of the given directions.
 */
__publicField(_a10, "PositivePerpendiculars", {
  [Direction2.Down]: [Direction2.East, Direction2.North],
  [Direction2.Up]: [Direction2.East, Direction2.North],
  [Direction2.North]: [Direction2.East, Direction2.Up],
  [Direction2.South]: [Direction2.East, Direction2.Up],
  [Direction2.East]: [Direction2.North, Direction2.Up],
  [Direction2.West]: [Direction2.North, Direction2.Up]
}), /**
 * The negative perpendicular directions of the given directions.
 */
__publicField(_a10, "NegativePerpendiculars", {
  [Direction2.Down]: [Direction2.West, Direction2.South],
  [Direction2.Up]: [Direction2.West, Direction2.South],
  [Direction2.North]: [Direction2.West, Direction2.Down],
  [Direction2.South]: [Direction2.West, Direction2.Down],
  [Direction2.East]: [Direction2.South, Direction2.Down],
  [Direction2.West]: [Direction2.South, Direction2.Down]
}), /**
 * All directions.
 */
__publicField(_a10, "Values", [
  Direction2.Down,
  Direction2.Up,
  Direction2.North,
  Direction2.South,
  Direction2.East,
  Direction2.West
]), _a10);
var log2 = Logger.getLogger("itemUtils", "bedrock-boost", "itemUtils");

// data/gametests/src/craftBuild/placeBuild.ts
import {
  BlockPermutation as BlockPermutation2,
  world as world8,
  system as system9,
  StructureAnimationMode,
  StructureRotation,
  UnloadedChunksError
} from "@minecraft/server";

// data/gametests/src/craftBuild/undoBuild.ts
import {
  world as world7,
  Player as Player3,
  StructureSaveMode as StructureSaveMode2,
  system as system8,
  ItemStack as ItemStack2
} from "@minecraft/server";
import { MessageFormData } from "@minecraft/server-ui";
function saveTerrain(structureLoc, entity, playerInv, buildStructure, dimension, corner1, corner2) {
  const blueprintItem = new ItemStack2("5fs_cb:restore_terrain", 1);
  blueprintItem.nameTag = `Undo Build: ${buildStructure.name}`;
  const entityId = entity.id.slice(-5);
  const itemId = buildStructure.entity.replace("5fs_cb:", "");
  const blueprintObject = {
    itemTypeId: buildStructure.item,
    craftItem: buildStructure,
    structureLoc,
    buildName: buildStructure.name,
    corner1,
    corner2,
    savedStructure: `mystructure:${itemId}_${entityId}`,
    structureOffset: new Vec3(corner1.x, corner1.y, corner1.z)
  };
  blueprintItem.setDynamicProperty("blueprint_data", JSON.stringify(blueprintObject));
  system8.runTimeout(() => {
    playerInv.addItem(blueprintItem);
  }, buildStructure.structureAnimationDuration ?? 20);
  try {
    world7.structureManager.createFromWorld(
      blueprintObject.savedStructure,
      dimension,
      corner1,
      corner2,
      {
        includeEntities: false,
        saveMode: StructureSaveMode2.World
      }
    );
  } catch (error) {
    console.error(
      `Failed to save Terrain. Data: ${JSON.stringify(blueprintObject)}`,
      error
    );
  }
}
async function restoreTerrainForm(player, blueprintData) {
  if (!blueprintData) {
    player.sendMessage("Error: Missing blueprint data.");
    return false;
  }
  const { buildName, corner1, corner2, structureLoc } = blueprintData;
  const messageForm = new MessageFormData().title(`Undo Build \xA7r\xA7l\xA7c${buildName}`).body(`Undo structure \xA7r\xA7n\xA7b${buildName}\xA7r located at [${Math.round(structureLoc.x)}, ${Math.round(structureLoc.y)}, ${Math.round(structureLoc.z)}].

\xA7lAll BLOCKS and ITEMS\xA7r within corners: [${Math.round(corner1.x)}, ${Math.round(corner1.y)}, ${Math.round(corner1.z)}] and [${Math.round(corner2.x)}, ${Math.round(corner2.y)}, ${Math.round(corner2.z)}] will be \xA7l\xA7cDELETED\xA7r.`).button1("\xA7l\xA7aConfirm").button2("\xA7l\xA7cReject");
  try {
    const formData = await messageForm.show(player);
    if (formData.canceled || formData.selection !== 0) {
      player.sendMessage("\xA7eUndo cancelled.");
      return false;
    }
    return true;
  } catch (error) {
    console.error("Error showing restore terrain form:", error);
    return false;
  }
}
world7.beforeEvents.itemUse.subscribe(({ source, itemStack: item }) => {
  if (item.typeId !== "5fs_cb:restore_terrain" || !(source instanceof Player3))
    return;
  system8.run(async () => {
    const getDynamicProperty = item.getDynamicProperty("blueprint_data");
    if (!getDynamicProperty)
      return;
    const parseProperty = JSON.parse(getDynamicProperty);
    const confirmed = await restoreTerrainForm(source, parseProperty);
    if (!confirmed)
      return;
    world7.structureManager.place(parseProperty.savedStructure, source.dimension, parseProperty.structureOffset, {
      includeEntities: false
    });
    await new Promise((resolve) => system8.run(resolve));
    const itemsInZone = source.dimension.getEntities({
      type: "minecraft:item",
      location: {
        x: (parseProperty.corner1.x + parseProperty.corner2.x) / 2,
        y: (parseProperty.corner1.y + parseProperty.corner2.y) / 2,
        z: (parseProperty.corner1.z + parseProperty.corner2.z) / 2
      },
      maxDistance: new Vec3(parseProperty.corner1).distance(new Vec3(parseProperty.corner2)) / 2
    });
    for (const itemEntity of itemsInZone) {
      itemEntity.remove();
    }
    const inv = source.getComponent("minecraft:inventory").container;
    for (let i = 0; i < inv.size; i++) {
      const it = inv.getItem(i);
      if (it?.typeId === "5fs_cb:restore_terrain") {
        inv.setItem(i, void 0);
        break;
      }
    }
    const buildItem = new ItemStack2(parseProperty.craftItem.item, 1);
    if (inv.emptySlotsCount > 0) {
      inv.addItem(buildItem);
      source.sendMessage(`\xA7bReturned ${parseProperty.buildName}`);
    } else {
      source.dimension.spawnItem(buildItem, source.location);
      source.sendMessage(`Inventory Full! Dropping: ${parseProperty.buildName}`);
    }
    source.sendMessage(`\xA7e\xA7l[!] \xA7r\xA7bRestoration Complete: \xA7e${parseProperty.buildName}`);
    source.playSound("build_fall");
    source.removeTag(approvalTag);
    world7.structureManager.delete(parseProperty.savedStructure);
  });
});
function expireItem(player, itemStack, damageToAdd) {
  try {
    const durabilityComp = itemStack.getComponent("minecraft:durability");
    if (!durabilityComp)
      return itemStack;
    durabilityComp.damage = Math.min(durabilityComp.damage + damageToAdd, durabilityComp.maxDurability);
    if (durabilityComp.damage >= durabilityComp.maxDurability) {
      player.removeTag(approvalTag);
      player.sendMessage("\xA7cThe time to undo the previous structure has expired.");
      return void 0;
    }
    const maxDurability = durabilityComp.maxDurability;
    const currentDurability = maxDurability - durabilityComp.damage;
    const totalSeconds = 300;
    const secondsPerDurability = totalSeconds / maxDurability;
    const remainingSecondsTotal = Math.floor(currentDurability * secondsPerDurability);
    const remainingMinutes = Math.floor(remainingSecondsTotal / 60);
    const remainingSeconds = remainingSecondsTotal % 60;
    const existingLore = itemStack.getLore() ?? [];
    let timeLoreFound = false;
    const updatedLore = existingLore.map((line) => {
      if (line.startsWith("\xA7cTime Remaining:")) {
        timeLoreFound = true;
        return `\xA7cTime Remaining: ${remainingMinutes}m ${remainingSeconds}s`;
      }
      return line;
    });
    if (!timeLoreFound) {
      updatedLore.push(`\xA7cTime Remaining: ${remainingMinutes}m ${remainingSeconds}s`);
    }
    itemStack.setLore(updatedLore);
    return itemStack;
  } catch (error) {
    console.error(`Error expiring item for player ${player.name}: ${error}`);
    return itemStack;
  }
}

// data/gametests/src/craftBuild/placeBuild.ts
import { MessageFormData as MessageFormData2 } from "@minecraft/server-ui";
var approvalTag = "5fs_pending_approval";
var VECTOR3_NORTH = new Vec3(0, 0, -1);
var VECTOR3_SOUTH = new Vec3(0, 0, 1);
var VECTOR3_EAST = new Vec3(1, 0, 0);
var VECTOR3_WEST = new Vec3(-1, 0, 0);
var protectedZones = /* @__PURE__ */ new Map();
function getStructureOffset(structureId) {
  const structureData = craftList.find((i) => i.structure === structureId);
  return {
    x: structureData?.structureCustomOffset.x ?? 0,
    y: structureData?.structureCustomOffset.y ?? 0,
    z: structureData?.structureCustomOffset.z ?? 0
  };
}
function resetHotbar(container, baseItems, accepted, craftItem) {
  let eggRemoved = false;
  for (let i = 0; i < 9; i++) {
    container.setItem(i, void 0);
    if (baseItems[i]) {
      if (accepted && craftItem && baseItems[i].typeId === craftItem.item && !eggRemoved) {
        eggRemoved = true;
      } else {
        container.setItem(i, baseItems[i]);
      }
    }
  }
}
function getBuildingData(source) {
  const prop = source.getDynamicProperty("buildingState");
  if (!prop)
    return null;
  try {
    return JSON.parse(prop);
  } catch (err) {
    return null;
  }
}
function updateParticlesForEntity(source, entityBuild, structure, offset) {
  const eLoc = entityBuild.location;
  const particleLocations = getParticleLocations(eLoc, structure, offset, entityBuild);
  particleLocations.forEach((loc) => {
    try {
      source.dimension.spawnParticle("5fs_cb:blue_square", { x: loc.x, y: loc.y + 0.25, z: loc.z });
    } catch (error) {
      if (error instanceof UnloadedChunksError)
        return;
    }
  });
}
async function showEnterConfirmationForm(player) {
  const form = new MessageFormData2().title("Enter Protected Build?").body("Would you like to enter this build?\n\n\xA7cWarning: Doing so will make the structure permanent and you will NOT be able to undo it.").button1("Yes").button2("No");
  const response = await form.show(player);
  if (response.canceled || response.selection === 1) {
    player.removeTag("_prompt_active");
    return;
  }
  const inventory = player.getComponent("inventory").container;
  for (let i = 0; i < inventory.size; i++) {
    const item = inventory.getItem(i);
    if (item?.typeId === "5fs_cb:restore_terrain") {
      const blueprintData = JSON.parse(item.getDynamicProperty("blueprint_data"));
      world8.structureManager.delete(blueprintData.savedStructure);
      inventory.setItem(i, void 0);
      break;
    }
  }
  player.removeTag(approvalTag);
  player.removeTag("_prompt_active");
  player.sendMessage("\xA7aThe structure is now permanent.");
}
function protectPlacedStructure(player, minBounds, maxBounds, structureSize) {
  protectedZones.set(player.id, { min: minBounds, max: maxBounds });
  const protectionInterval = system9.runInterval(() => {
    if (!player.isValid || !player.hasTag(approvalTag)) {
      system9.clearRun(protectionInterval);
      protectedZones.delete(player.id);
      return;
    }
    const currentZone = protectedZones.get(player.id);
    if (!currentZone)
      return;
    const width = currentZone.max.x - currentZone.min.x;
    const height = currentZone.max.y - currentZone.min.y;
    const depth = currentZone.max.z - currentZone.min.z;
    const spaceDiagonal = Math.sqrt(width ** 2 + height ** 2 + depth ** 2);
    const radius = spaceDiagonal / 2;
    const centerX = (currentZone.min.x + currentZone.max.x) / 2;
    const centerY = (currentZone.min.y + currentZone.max.y) / 2;
    const centerZ = (currentZone.min.z + currentZone.max.z) / 2;
    const nearbyEntities = player.dimension.getEntities({ location: { x: centerX, y: centerY, z: centerZ }, maxDistance: radius });
    for (const entity of nearbyEntities) {
      const loc = entity.location;
      if (loc.x >= currentZone.min.x && loc.x < currentZone.max.x + 1 && loc.y >= currentZone.min.y && loc.y < currentZone.max.y + 1 && loc.z >= currentZone.min.z && loc.z < currentZone.max.z + 1) {
        if (entity.id === player.id) {
          if (!player.hasTag("_prompt_active")) {
            player.addTag("_prompt_active");
            showEnterConfirmationForm(player);
          }
        }
        const dx1 = loc.x - currentZone.min.x;
        const dx2 = currentZone.max.x + 1 - loc.x;
        const dz1 = loc.z - currentZone.min.z;
        const dz2 = currentZone.max.z + 1 - loc.z;
        const min_dist = Math.min(dx1, dx2, dz1, dz2);
        let newLoc = { ...loc };
        if (min_dist === dx1)
          newLoc.x = currentZone.min.x - 0.5;
        else if (min_dist === dx2)
          newLoc.x = currentZone.max.x + 1.5;
        else if (min_dist === dz1)
          newLoc.z = currentZone.min.z - 0.5;
        else
          newLoc.z = currentZone.max.z + 1.5;
        entity.tryTeleport(newLoc);
        if (entity.typeId === "minecraft:player") {
          const targetPlayer = entity;
          targetPlayer.onScreenDisplay.setActionBar("\xA7cThis area is temporarily protected.");
          targetPlayer.playSound("note.bass", { location: targetPlayer.location });
        }
      }
    }
  }, 1);
}
world8.afterEvents.itemUse.subscribe(({ itemStack, source }) => {
  if (source.typeId !== "minecraft:player" || source.hasTag(approvalTag))
    return;
  const structureItem = craftList.find((i) => itemStack.typeId === i.item);
  if (!structureItem)
    return;
  source.setDynamicProperty("buildingState", void 0);
  const invComp = source.getComponent("inventory");
  const plyrInv = invComp.container;
  const plyrItems = [];
  const getBlock = source.getBlockFromViewDirection({ excludePermutations: [BlockPermutation2.resolve("minecraft:water")] });
  if (!getBlock)
    return;
  const blockLoc = getBlock.block.location;
  const entityBuild = source.dimension.spawnEntity(structureItem.entity, { x: blockLoc.x + 0.5, y: blockLoc.y + 1, z: blockLoc.z + 0.5 });
  const entityBuildData = { owner: source.id, buildStructure: structureItem.structure };
  let buildingData = { state: "isBuilding", buildStructure: structureItem.structure, entityId: entityBuild.id, entityLocation: blockLoc };
  entityBuild.setDynamicProperty("entityBuildData", JSON.stringify(entityBuildData));
  for (let i = 0; i < 9; i++) {
    const item = plyrInv.getItem(i);
    if (item)
      plyrItems.push(item);
  }
  entityBuild.teleport(entityBuild.location, { facingLocation: source.location });
  itemDatabase.set("items_array_0", plyrItems);
  setBuildSettings(source);
  source.setDynamicProperty("buildingState", JSON.stringify(buildingData));
  const structure = world8.structureManager.get(structureItem.structure);
  const offset = getStructureOffset(structureItem.structure);
  startParticleLoop(entityBuild, source, structure, offset);
});
world8.afterEvents.itemUse.subscribe(({ itemStack, source }) => {
  if (source.typeId !== "minecraft:player")
    return;
  const settingItem = buildSettings.find((i) => i.setting === itemStack.typeId);
  if (!settingItem)
    return;
  const cooldownComp = itemStack.getComponent("cooldown");
  if (cooldownComp && cooldownComp.getCooldownTicksRemaining(source) > 0)
    return;
  const container = source.getComponent("inventory").container;
  const baseItems = itemDatabase.get("items_array_0");
  const buildingData = getBuildingData(source);
  if (!buildingData)
    return;
  const entityBuild = source.dimension.getEntities({ location: source.location, maxDistance: 64, excludeTypes: ["minecraft:xp_orb", "minecraft:item", "5fs_cb:item_storage"] }).find((e) => e.id === buildingData.entityId);
  if (!entityBuild) {
    source.playSound("note.bass");
    source.sendMessage("\xA7e\xA7l[!] \xA7r\xA7cYou are too far away from the build location!");
    return;
  }
  const buildLoc = new Vec3(entityBuild.location);
  const structure = world8.structureManager.get(buildingData.buildStructure);
  const offset = getStructureOffset(buildingData.buildStructure);
  const updateParticles = () => updateParticlesForEntity(source, entityBuild, structure, offset);
  const moveBuild = (direction, message) => {
    source.sendMessage(message);
    const newLoc = new Vec3(entityBuild.location).add(direction);
    entityBuild.tryTeleport(newLoc);
    source.playSound("note.bit");
    updateParticles();
  };
  const actions = {
    "5fs_cb:build_reject": () => {
      resetHotbar(container, baseItems, false);
      source.sendMessage("\xA7e\xA7l[!] \xA7r\xA7cBuild Rejected!");
      source.setDynamicProperty("buildingState", void 0);
      source.playSound("note.bass");
      entityBuild.remove();
    },
    "5fs_cb:build_move_west": () => moveBuild(VECTOR3_WEST, "\xA7e\xA7l[!] \xA7r\xA7bBuild Moved West!"),
    "5fs_cb:build_move_north": () => moveBuild(VECTOR3_NORTH, "\xA7e\xA7l[!] \xA7r\xA7bBuild Moved North!"),
    "5fs_cb:build_move_south": () => moveBuild(VECTOR3_SOUTH, "\xA7e\xA7l[!] \xA7r\xA7bBuild Moved South!"),
    "5fs_cb:build_move_east": () => moveBuild(VECTOR3_EAST, "\xA7e\xA7l[!] \xA7r\xA7bBuild Moved East!"),
    "5fs_cb:build_rotate_clockwise": () => {
      source.sendMessage("\xA7e\xA7l[!] \xA7r\xA7bBuild Rotated Clockwise!");
      source.playSound("note.hat");
      const rotation = entityBuild.getRotation();
      let newYaw = rotation.y + 90;
      if (newYaw > 180)
        newYaw -= 360;
      entityBuild.setRotation({ x: rotation.x, y: newYaw });
      updateParticles();
    },
    "5fs_cb:build_rotate_counterclockwise": () => {
      source.sendMessage("\xA7e\xA7l[!] \xA7r\xA7bBuild Rotated Counterclockwise!");
      source.playSound("note.hat");
      const rotation = entityBuild.getRotation();
      let newYaw = rotation.y - 90;
      if (newYaw < -180)
        newYaw += 360;
      entityBuild.setRotation({ x: rotation.x, y: newYaw });
      updateParticles();
    },
    "5fs_cb:build_accept": () => {
      const craftData = craftList?.find((i) => i.structure === buildingData.buildStructure);
      let adjustedSize = { x: structure.size.x, z: structure.size.z };
      if (getStructureRotationFromEntity(entityBuild) === StructureRotation.Rotate90 || getStructureRotationFromEntity(entityBuild) === StructureRotation.Rotate270) {
        adjustedSize = { x: structure.size.z, z: structure.size.x };
      }
      const buildOffset = { x: buildLoc.x - adjustedSize.x / 2 + offset.x, y: buildLoc.y + offset.y, z: buildLoc.z - adjustedSize.z / 2 + offset.z };
      const minBounds = { x: Math.floor(buildOffset.x), y: Math.floor(buildOffset.y), z: Math.floor(buildOffset.z) };
      const maxBounds = {
        x: Math.floor(buildOffset.x + adjustedSize.x - 1),
        y: Math.floor(buildOffset.y + structure.size.y - 1),
        z: Math.floor(buildOffset.z + adjustedSize.z - 1)
      };
      resetHotbar(container, baseItems, true, craftData);
      saveTerrain(entityBuild.location, entityBuild, container, craftData, source.dimension, minBounds, maxBounds);
      world8.structureManager.place(structure, source.dimension, buildOffset, {
        includeEntities: false,
        rotation: getStructureRotationFromEntity(entityBuild),
        animationMode: craftData.structureAnimationMode ?? StructureAnimationMode.None,
        animationSeconds: craftData.structureAnimationDuration ?? 0
      });
      system9.run(() => {
        source.sendMessage("\xA7e\xA7l[!] \xA7r\xA7aBuild Accepted!");
        source.playSound("random.levelup");
        source.setDynamicProperty("buildingState", void 0);
        entityBuild.remove();
        source.addTag(approvalTag);
        protectPlacedStructure(source, minBounds, maxBounds, structure.size);
      });
    }
  };
  const actionHandler = actions[settingItem.setting];
  if (actionHandler)
    actionHandler();
});
world8.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  const { player, block } = ev;
  const playerLoc = player.location;
  const blockLoc = block.location;
  for (const zone of protectedZones.values()) {
    const { min, max } = zone;
    const isPlayerInside = playerLoc.x >= min.x && playerLoc.x <= max.x && playerLoc.y >= min.y && playerLoc.y <= max.y && playerLoc.z >= min.z && playerLoc.z <= max.z;
    const isBlockInside = blockLoc.x >= min.x && blockLoc.x <= max.x && blockLoc.y >= min.y && blockLoc.y <= max.y && blockLoc.z >= min.z && blockLoc.z <= max.z;
    if (isPlayerInside || isBlockInside) {
      ev.cancel = true;
      return;
    }
  }
});
world8.beforeEvents.playerBreakBlock.subscribe((ev) => {
  const { block } = ev;
  const blockLoc = block.location;
  for (const zone of protectedZones.values()) {
    const { min, max } = zone;
    if (blockLoc.x >= min.x && blockLoc.x <= max.x && blockLoc.y >= min.y && blockLoc.y <= max.y && blockLoc.z >= min.z && blockLoc.z <= max.z) {
      ev.cancel = true;
      return;
    }
  }
});

// data/gametests/src/craftBuild/index.ts
var itemDatabase = new QIDB("player_items");
var buildSettings = [
  { invSlot: 0, setting: "5fs_cb:build_reject" },
  { invSlot: 1, setting: "5fs_cb:build_move_west" },
  { invSlot: 2, setting: "5fs_cb:build_move_north" },
  { invSlot: 3, setting: "5fs_cb:build_move_south" },
  { invSlot: 4, setting: "5fs_cb:build_move_east" },
  { invSlot: 6, setting: "5fs_cb:build_rotate_clockwise" },
  { invSlot: 7, setting: "5fs_cb:build_rotate_counterclockwise" },
  { invSlot: 8, setting: "5fs_cb:build_accept" }
];
function setBuildSettings(player) {
  const blankItem = new ItemStack4("5fs_cb:blank", 1);
  const playerInv = player.getComponent("minecraft:inventory").container;
  for (let i = 0; i < 9; i++) {
    blankItem.lockMode = ItemLockMode.slot;
    playerInv.setItem(i, blankItem);
  }
  buildSettings.forEach((settingItem) => {
    const settingStack = new ItemStack4(settingItem.setting, 1);
    settingStack.lockMode = ItemLockMode.slot;
    playerInv.setItem(settingItem.invSlot, settingStack);
  });
}
function getStructureRotationFromEntity(entity) {
  const rotationY = entity.getRotation().y;
  if (rotationY >= -45 && rotationY < 45)
    return StructureRotation2.None;
  if (rotationY >= 45 && rotationY < 135)
    return StructureRotation2.Rotate90;
  if (rotationY >= -135 && rotationY < -45)
    return StructureRotation2.Rotate270;
  return StructureRotation2.Rotate180;
}
function rotatePoint(point, origin, angle) {
  const rad = angle * (Math.PI / 180);
  const dx = point.x - origin.x;
  const dz = point.z - origin.z;
  const rotatedX = dx * Math.cos(rad) - dz * Math.sin(rad);
  const rotatedZ = dx * Math.sin(rad) + dz * Math.cos(rad);
  return new Vec3(origin.x + rotatedX, point.y, origin.z + rotatedZ);
}
function startParticleLoop(entityBuild, source, structure, offset) {
  const particleLoopId = system10.runInterval(() => {
    if (!entityBuild.isValid) {
      system10.clearRun(particleLoopId);
      return;
    }
    const eLoc = entityBuild.location;
    const particleLocations = getParticleLocations(eLoc, structure, offset, entityBuild);
    particleLocations.forEach((loc) => {
      try {
        source.dimension.spawnParticle("5fs_cb:blue_square", {
          x: loc.x,
          y: eLoc.y + 0.25,
          z: loc.z
        });
      } catch (error) {
        if (error instanceof LocationInUnloadedChunkError) {
          return;
        }
      }
    });
  }, 20);
}
function getParticleLocations(center, structure, offset, entity) {
  const locations = [];
  const baseX = Math.floor(center.x + offset.x);
  const baseY = Math.floor(center.y + offset.y);
  const baseZ = Math.floor(center.z + offset.z);
  const halfX = Math.floor(structure.size.x / 2);
  const halfZ = Math.floor(structure.size.z / 2);
  const minX = baseX - halfX - 1;
  const maxX = baseX + halfX + 1;
  const minZ = baseZ - halfZ - 1;
  const maxZ = baseZ + halfZ + 1;
  for (let x = minX; x <= maxX; x++) {
    locations.push(new Vec3(x + 0.5, baseY, minZ + 0.5));
  }
  for (let x = minX; x <= maxX; x++) {
    locations.push(new Vec3(x + 0.5, baseY, maxZ + 0.5));
  }
  for (let z = minZ + 1; z < maxZ; z++) {
    locations.push(new Vec3(minX + 0.5, baseY, z + 0.5));
  }
  for (let z = minZ + 1; z < maxZ; z++) {
    locations.push(new Vec3(maxX + 0.5, baseY, z + 0.5));
  }
  const origin = new Vec3(baseX + 0.5, baseY, baseZ + 0.5);
  const rotation = entity.getRotation();
  const yaw = rotation.y;
  let angle = 0;
  if (yaw >= -45 && yaw < 45) {
    angle = 0;
  } else if (yaw >= 45 && yaw < 135) {
    angle = 90;
  } else if (yaw >= 135 || yaw < -135) {
    angle = 180;
  } else {
    angle = -90;
  }
  const rotatedLocations = locations.map((loc) => {
    const rotated = rotatePoint(loc, origin, angle);
    return new Vec3(Math.floor(rotated.x) + 0.5, rotated.y, Math.floor(rotated.z) + 0.5);
  });
  const viewDirection = new Vec3(entity.getViewDirection()).normalize();
  rotatedLocations.sort((a, b) => {
    const aRelative = a.subtract(origin);
    const bRelative = b.subtract(origin);
    return bRelative.dot(viewDirection) - aRelative.dot(viewDirection);
  });
  return rotatedLocations;
}
var craftList = [
  {
    item: "5fs_cb:bank_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:bank",
    name: "Bank",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 15,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:barn_0_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:barn_0",
    name: "Animal Barn",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:barn_1_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:barn_1",
    name: "Farmers Barn",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:barn_2_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:barn_2",
    name: "Farmers Sanctuary",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:bedbug_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:bedbug",
    name: "Bedbug",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:bridge_0_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:bridge_0",
    name: "Castle Wall",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:bridge_1_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:bridge_1",
    name: "Castle Cornerstone",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:bunker_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:bunker",
    name: "Bunker",
    structureCustomOffset: { x: 8, y: -24, z: -2 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:creeperhead_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:creeperHead",
    name: "Creeper Head",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:dragonhead_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:dragonHead",
    name: "Sea Dragons Head",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:endportal_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:endPortal",
    name: "End Portal",
    structureCustomOffset: { x: 0, y: -3, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:house_0_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:house_0",
    name: "Urban Farmhouse",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:house_1_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:house_1",
    name: "Suburban House",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:house_2_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:house_2",
    name: "Urban House",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:junglepyramid_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:junglePyramid",
    name: "Jungle Pyramid",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:largepyramid_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:largePyramid",
    name: "Desert Pyramid",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:luckyblock_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:luckyBlock",
    name: "Lucky Block",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:modernhotel_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:modernHotel",
    name: "Modern Hotel",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:modernhouse_0_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:modernhouse_0",
    name: "Mini Mansion",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:modernhouse_1_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:modernHouse_1",
    name: "Large Mansion",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:netherportal_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:netherPortal",
    name: "Nether Portal",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:pyramid_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:pyramid",
    name: "Pyramid",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:restaurant_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:restaurant",
    name: "Restaurant",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:skull_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:skull",
    name: "Skull",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:smalltower_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:smallTower",
    name: "Lakeside Pagoda",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:sportsbar_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:sportsBar",
    name: "Sports Cafe",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:watchtower_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:watchTower",
    name: "Hunters Watchtower",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:wizardhouse_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:wizardHouse",
    name: "Wizard House",
    structureCustomOffset: { x: 0, y: 0, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  },
  {
    item: "5fs_cb:zombiehand_craft",
    entity: "5fs_cb:structure",
    structure: "5fs_cb/cb:zombieHand",
    name: "Zombie Hand",
    structureCustomOffset: { x: 0, y: -1, z: 0 },
    structureAnimationMode: StructureAnimationMode2.Layers,
    structureAnimationDuration: 3,
    lore: "Press use in a flat area to load the structure"
  }
];
world9.afterEvents.entityDie.subscribe(({ damageSource, deadEntity }) => {
  const entity = damageSource.damagingEntity;
  if (entity?.typeId === "minecraft:player" && deadEntity.typeId === "minecraft:ender_dragon") {
    entity.runCommand("playsound defeated_dragon @s[tag=!world_init,tag=!end_portal_recipe]"), entity.runCommand("give @s[tag=!world_init,tag=!end_portal_recipe] 5fs_cb:endportal_craft 1"), entity.runCommand("recipe give @s[tag=!world_init,tag=!end_portal_recipe] 5fs_cb:end_portal_recipe"), entity.runCommand(`tellraw @s[tag=!world_init,tag=!end_portal_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: End of the road! You've defeated the Ender Dragon, for this the \xA7lEnd Portal\xA7r structure is now unlocked. This structure has been given to you."}]}`), entity.runCommand("tag @s add end_portal_recipe");
  }
});

// data/gametests/src/biomeDetection.js
import { system as system11, world as world10, EntityComponentTypes, EquipmentSlot as EquipmentSlot2, ItemStack as ItemStack5 } from "@minecraft/server";
var EquipmentSlots = {
  Head: EquipmentSlot2.Head,
  Chest: EquipmentSlot2.Chest,
  Legs: EquipmentSlot2.Legs,
  Feet: EquipmentSlot2.Feet,
  Mainhand: EquipmentSlot2.Mainhand,
  Offhand: EquipmentSlot2.Offhand,
  Body: EquipmentSlot2.Body
};
function checkEquipment(source, slotName) {
  const equipment = source.getComponent(EntityComponentTypes.Equippable);
  if (!equipment) {
    return void 0;
  }
  const slot = EquipmentSlots[slotName];
  if (!slot) {
    return void 0;
  }
  const item = equipment.getEquipment(slot);
  if (!item) {
    return void 0;
  }
  return item || void 0;
}
var biomeEntity = "5fs_cb:biome_type";
system11.runInterval(() => {
  for (const player of world10.getAllPlayers()) {
    const dragonHead = checkEquipment(player, "Head");
    if (dragonHead?.typeId === "minecraft:dragon_head") {
      player.runCommand("give @s[tag=!world_init,tag=!dragon_head_recipe] 5fs_cb:dragonhead_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!dragon_head_recipe] 5fs_cb:dragon_head_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!dragon_head_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: The \xA7lDragon Head\xA7r! For wearing this head, you have unlocked the \xA7lDragon Head\xA7r structure. This structure has been given to you."}]}'), player.runCommand("tag @s add dragon_head_recipe");
    }
    const entity = player.dimension.spawnEntity(biomeEntity, player.location);
    const biome = entity.getProperty("5fs.cb.itembehavior:biome_type");
    switch (biome) {
      case 0:
        player.runCommand("give @s[tag=!world_init,tag=!watchtower_recipe] 5fs_cb:watchtower_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!watchtower_recipe] 5fs_cb:watchtower_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!watchtower_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Taiga biome! For this, you have unlocked the \xA7lHunters Watchtower\xA7r structure. This structure has been given to you."}]}'), player.runCommand("tag @s add watchtower_recipe");
        break;
      case 1:
        player.runCommand("give @s[tag=!world_init,tag=!barn_recipe] 5fs_cb:barn_0_craft 1"), player.runCommand("give @s[tag=!world_init,tag=!barn_recipe] 5fs_cb:barn_1_craft 1"), player.runCommand("give @s[tag=!world_init,tag=!barn_recipe] 5fs_cb:barn_2_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!barn_recipe] 5fs_cb:barn_0_recipe"), player.runCommand("recipe give @s[tag=!world_init,tag=!barn_recipe] 5fs_cb:barn_1_recipe"), player.runCommand("recipe give @s[tag=!world_init,tag=!barn_recipe] 5fs_cb:barn_2_recipe"), player.runCommand(`tellraw @s[tag=!world_init,tag=!barn_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Savannah biome! For this, you have unlocked the \xA7lFarmer's Dream\xA7r set. The following structures have been given to you: \xA7lAnimal Barn\xA7r, the \xA7lFarmers Barn\xA7r, and the \xA7lFarmers Sanctuary\xA7r."}]}`), player.runCommand("tag @s add barn_recipe");
        break;
      case 2:
        player.runCommand("give @s[tag=!world_init,tag=!restaurant_recipe] 5fs_cb:restaurant_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!restaurant_recipe] 5fs_cb:restaurant_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!restaurant_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Beach biome! For this, you have unlocked the \xA7lRestaurant\xA7r structure. This structure has been given to you."}]}'), player.runCommand("tag @s add restaurant_recipe");
        break;
      case 3:
        player.runCommand("give @s[tag=!world_init,tag=!bunker_recipe] 5fs_cb:bunker_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!bunker_recipe] 5fs_cb:bunker_recipe"), player.runCommand(`tellraw @s[tag=!world_init,tag=!bunker_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rYou found a Roofed Forest! That unlocks the \xA7lBunker\xA7r structure. I've handed it over-looks like you're ready for anything now!"}]}`), player.runCommand("tag @s add bunker_recipe");
        break;
      case 4:
        player.runCommand("give @s[tag=!world_init,tag=!pyramid_recipe] 5fs_cb:pyramid_craft 1"), player.runCommand("give @s[tag=!world_init,tag=!pyramid_recipe] 5fs_cb:largepyramid_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!pyramid_recipe] 5fs_cb:pyramid_recipe"), player.runCommand("recipe give @s[tag=!world_init,tag=!pyramid_recipe] 5fs_cb:large_pyramid_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!pyramid_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Desert biome! For this, you have unlocked the \xA7lPyramid\xA7r structures. This structure has been given to you."}]}'), player.runCommand("tag @s add pyramid_recipe");
        break;
      case 5:
        player.runCommand("give @s[tag=!world_init,tag=!zombiehand_recipe] 5fs_cb:zombiehand_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!zombiehand_recipe] 5fs_cb:zombiehand_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!zombiehand_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Extreme Hills Biome! For this, you have unlocked the \xA7lZombie Hand\xA7r structure. This structure has been given to you."}]}'), player.runCommand("tag @s add zombiehand_recipe");
        break;
      case 6:
        player.runCommand("give @s[tag=!world_init,tag=!bedbug_recipe] 5fs_cb:bedbug_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!bedbug_recipe] 5fs_cb:bedbug_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!bedbug_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Swamp! For this, you have unlocked the \xA7lBedbug\xA7r structure. This structure has been given to you."}]}'), player.runCommand("tag @s add bedbug_recipe");
        break;
      case 7:
        player.runCommand("give @s[tag=!world_init,tag=!nether_portal_recipe] 5fs_cb:netherportal_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!nether_portal_recipe] 5fs_cb:nether_portal_recipe"), player.runCommand(`tellraw @s[tag=!world_init,tag=!nether_portal_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: The Nether? You've entered the Nether for the first time! The \xA7lNether Portal\xA7r structure is now unlocked. This structure has been given to you."}]}`), player.runCommand("tag @s add nether_portal_recipe");
        break;
      case 8:
        player.runCommand("give @s[tag=!world_init,tag=!jungle_pyramid_recipe] 5fs_cb:junglepyramid_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!jungle_pyramid_recipe] 5fs_cb:jungle_pyramid_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!jungle_pyramid_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Jungle biome! For this, you have unlocked the \xA7lJungle Pyramid\xA7r structure. This structure has been given to you."}]}'), player.runCommand("tag @s add jungle_pyramid_recipe");
        break;
    }
  }
}, 60);
async function sleep(ticks) {
  return new Promise((resolve) => system11.runTimeout(() => resolve(void 0), ticks));
}
async function delayedMessage(source, message, delay = 20, target = null) {
  await sleep(delay);
  if (target)
    return target.sendMessage(message);
  source.sendMessage(message);
}
world10.afterEvents.playerSpawn.subscribe((event) => {
  const { player, initialSpawn } = event;
  if (!initialSpawn)
    return;
  delayedMessage(player, "\xA7l[\xA7eCraftable Builds\xA7f]\xA7r\xA7e Add-On Loaded!\xA7r", 100);
  const giveBook = system11.runInterval(() => {
    try {
      if (!player.isOnGround)
        return;
      if (player.hasTag("5fs_cb:start_guidebook")) {
        system11.clearRun(giveBook);
        return;
      }
      delayedMessage(player, "\xA7l[\xA7eCraftable Builds\xA7f]\xA7r\xA7a You have been given a Guidebook!\xA7r", 120);
      const inventory = player.getComponent("minecraft:inventory");
      if (!inventory)
        return;
      const { container } = inventory;
      const guideBookItem = new ItemStack5("5fs_cb:guidebook", 1);
      guideBookItem.keepOnDeath = true;
      if (container.emptySlotsCount > 0) {
        container.addItem(guideBookItem);
      } else {
        player.dimension.spawnItem(guideBookItem, player.location);
      }
      player.addTag("5fs_cb:start_guidebook");
      system11.clearRun(giveBook);
    } catch (e) {
    }
  }, 1);
});

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/Guidebook.js
import { system as system15 } from "@minecraft/server";
import { MessageFormData as MessageFormData3 } from "@minecraft/server-ui";
import { ActionFormData as ActionFormData2 } from "@minecraft/server-ui";

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/PageManager.js
import { system as system12 } from "@minecraft/server";

// data/gametests/node_modules/@5-frame-studios/logger/dist/Logger.js
var Logger2 = class {
  /**
   * Create a new Logger instance.
   * @param config - Logger configuration options.
   */
  constructor(config = {}) {
    this.logLevel = config.logLevel ?? "info";
    this.outputMode = config.outputMode ?? "console";
    this.prefix = config.prefix ?? "[Logger]";
    this.colors = {
      debug: "\xA77",
      info: "\xA79",
      warn: "\xA7e",
      error: "\xA7c",
      ...config.colors ?? {}
    };
    this.allowedSources = config.allowedSources ? new Set(config.allowedSources) : null;
    this.source = config.source ?? "";
    this.world = config.world;
    this.getPlayers = config.getPlayers;
    this.customOutput = config.customOutput;
  }
  /**
   * Set the minimum log level. Messages below this level will be ignored.
   * @param level - The minimum log level ('debug', 'info', 'warn', 'error').
   */
  setLogLevel(level) {
    this.logLevel = level;
  }
  /**
   * Set the output mode for log messages.
   * @param mode - Output mode ('console', 'chat', 'scoreboard', 'custom').
   */
  setOutputMode(mode) {
    this.outputMode = mode;
  }
  /**
   * Set the prefix for all log messages.
   * @param prefix - Prefix string.
   */
  setPrefix(prefix) {
    this.prefix = prefix;
  }
  /**
   * Set custom colors for log levels.
   * @param colors - Partial color mapping for log levels (Minecraft color codes).
   */
  setColors(colors) {
    this.colors = { ...this.colors, ...colors };
  }
  /**
   * Restrict logging to specific sources.
   * @param sources - Array of allowed source names, or null for no restriction.
   */
  setAllowedSources(sources) {
    this.allowedSources = sources ? new Set(sources) : null;
  }
  /**
   * Set the source label for this logger instance.
   * @param source - Source name.
   */
  setSource(source) {
    this.source = source;
  }
  /**
   * Set the world object for this logger instance.
   * @param world - Minecraft world object.
   */
  setWorld(world16) {
    this.world = world16;
  }
  /**
   * Set the getPlayers function for this logger instance.
   * @param getPlayers - Function returning an array of player objects.
   */
  setGetPlayers(getPlayers) {
    this.getPlayers = getPlayers;
  }
  /**
   * Set the custom output function for this logger instance.
   * @param fn - Custom output function.
   */
  setCustomOutput(fn) {
    this.customOutput = fn;
  }
  /**
   * Log a debug-level message.
   * @param message - The message or object to log.
   */
  debug(message) {
    this._log(message, "debug");
  }
  /**
   * Log an info-level message.
   * @param message - The message or object to log.
   */
  info(message) {
    this._log(message, "info");
  }
  /**
   * Log a warning-level message.
   * @param message - The message or object to log.
   */
  warn(message) {
    this._log(message, "warn");
  }
  /**
   * Log an error-level message.
   * @param message - The message or object to log.
   */
  error(message) {
    this._log(message, "error");
  }
  /**
   * Internal log handler. Applies filtering, formatting, and output.
   * @param message - The message or object to log.
   * @param level - The log level for this message.
   */
  _log(message, level) {
    const levels = { debug: 0, info: 1, warn: 2, error: 3 };
    if (levels[level] < levels[this.logLevel])
      return;
    if (this.allowedSources && this.source && !this.allowedSources.has(this.source))
      return;
    let prefix = this.prefix;
    let color = this.colors[level] || "";
    let sourceTag = this.source ? `[${this.source}]` : "";
    switch (level) {
      case "debug":
        prefix += " \xA77[DEBUG]";
        break;
      case "info":
        prefix += " \xA79[INFO]";
        break;
      case "warn":
        prefix += " \xA7e[WARNING]";
        break;
      case "error":
        prefix += " \xA7c[ERROR]";
        break;
    }
    if (typeof message !== "string") {
      try {
        message = JSON.stringify(message);
      } catch {
        message = String(message);
      }
    }
    const chatMsg = `${prefix} ${sourceTag} ${color}${message}`.trim();
    switch (this.outputMode) {
      case "console":
        switch (level) {
          case "debug":
            console.warn(this.prefix, sourceTag, "[DEBUG]", message);
            break;
          case "info":
            console.warn(this.prefix, sourceTag, "[INFO]", message);
            break;
          case "warn":
            console.warn(this.prefix, sourceTag, "[WARNING]", message);
            break;
          case "error":
            console.error(this.prefix, sourceTag, "[ERROR]", message);
            break;
        }
        break;
      case "chat": {
        const world16 = this.world;
        const getPlayers = this.getPlayers;
        if (!world16 && !getPlayers) {
          throw new Error("Logger: world or getPlayers must be supplied for chat output mode.");
        }
        try {
          if (world16 && typeof world16.sendMessage === "function") {
            world16.sendMessage(chatMsg);
          } else if (getPlayers) {
            for (const player of getPlayers()) {
              try {
                player.sendMessage(chatMsg);
              } catch {
              }
            }
          }
        } catch (err) {
          console.error(this.prefix, sourceTag, "[CHAT-ERROR]", message, err);
        }
        break;
      }
      case "scoreboard": {
        const world16 = this.world;
        const getPlayers = this.getPlayers;
        if (!world16 && !getPlayers) {
          throw new Error("Logger: world or getPlayers must be supplied for scoreboard output mode.");
        }
        let truncated = message.substring(0, 32);
        try {
          if (world16 && world16.scoreboard && typeof world16.scoreboard.addObjective === "function") {
            try {
              world16.scoreboard.addObjective("log", "log");
            } catch {
            }
          }
          const players = getPlayers ? getPlayers() : world16 && typeof world16.getPlayers === "function" ? world16.getPlayers() : [];
          for (const player of players) {
            try {
              if (typeof player.runCommand === "function") {
                player.runCommand(`scoreboard players set @s log 1`);
                player.runCommand(`scoreboard players set "${truncated}" log 1`);
              }
            } catch {
            }
          }
        } catch (err) {
          console.error(this.prefix, sourceTag, "[SCOREBOARD-ERROR]", message, err);
        }
        break;
      }
      case "custom":
        if (typeof this.customOutput === "function") {
          this.customOutput(level, message, { prefix, source: this.source, raw: message });
        }
        break;
    }
  }
};

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/SharedLogger.js
var SharedLogger = class _SharedLogger {
  constructor() {
    this.logger = new Logger2({
      logLevel: "debug",
      outputMode: "console",
      prefix: "[Guidebook]"
    });
  }
  /**
   * Gets the singleton instance of the shared logger.
   */
  static getInstance() {
    if (!_SharedLogger.instance) {
      _SharedLogger.instance = new _SharedLogger();
    }
    return _SharedLogger.instance;
  }
  /**
   * Sets the global log level for the entire guidebook system.
   *
   * @param logLevel The log level to set
   */
  setLogLevel(logLevel) {
    this.logger.setLogLevel(logLevel);
  }
  /**
   * Gets the underlying logger instance.
   */
  getLogger() {
    return this.logger;
  }
  // Proxy methods to the underlying logger
  debug(message) {
    this.logger.debug(message);
  }
  info(message) {
    this.logger.info(message);
  }
  warn(message) {
    this.logger.warn(message);
  }
  error(message) {
    this.logger.error(message);
  }
};
var sharedLogger = SharedLogger.getInstance();

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/PageManager.js
var PageManager = class {
  /**
   * Creates a new PageManager instance.
   *
   * @param guidebook The parent guidebook instance
   *
   * @example
   * ```typescript
   * const pageManager = new PageManager(guidebook);
   * ```
   */
  constructor(guidebook2) {
    this.guidebook = guidebook2;
  }
  /**
   * Performs a comprehensive search across all guidebook pages.
   *
   * This method searches through page titles, body content, button text, and field labels
   * to find pages that match the search term. Results are ranked by relevance and
   * displayed in a dynamic search results page.
   *
   * The search algorithm prioritizes matches in the following order:
   * 1. Title matches (highest priority - 10 points)
   * 2. Body content matches (medium priority - 5 points)
   * 3. Button text matches (lower priority - 3 points)
   * 4. Field label matches (lowest priority - 2 points)
   *
   * @param player The player performing the search
   * @param searchTerm The term to search for (case-insensitive)
   *
   * @example
   * ```typescript
   * // Search for pages containing "tutorial"
   * guidebook.pageManager.performSearch(player, "tutorial");
   *
   * // Search for pages containing "weapon"
   * guidebook.pageManager.performSearch(player, "weapon");
   * ```
   */
  performSearch(player, searchTerm) {
    sharedLogger.debug(` Search initiated by ${player.name} with term: "${searchTerm}"`);
    sharedLogger.debug(` Search term type: ${typeof searchTerm}, length: ${searchTerm?.length}`);
    if (!searchTerm || typeof searchTerm !== "string" || searchTerm.trim().length === 0) {
      sharedLogger.warn(`[SEARCH DEBUG] Invalid search term - empty or invalid type`);
      Guidebook.showPopup(player, "Search", "Please enter a search term.");
      return;
    }
    const term = searchTerm.toLowerCase().trim();
    sharedLogger.debug(` Normalized search term: "${term}"`);
    const results = [];
    const pageDefs = this.guidebook.getPageDefs();
    const totalPages = pageDefs.size;
    sharedLogger.debug(` Starting search through ${totalPages} total pages`);
    let pagesChecked = 0;
    let pagesWithMatches = 0;
    for (const [pageId, pageDef] of pageDefs) {
      pagesChecked++;
      sharedLogger.debug(` Checking page ${pagesChecked}/${totalPages}: "${pageId}"`);
      if (pageDef.showInSearch === false) {
        sharedLogger.debug(`   Skipping page "${pageId}" - showInSearch is false`);
        continue;
      }
      let activePageDef;
      try {
        activePageDef = this._resolvePageVersion(player, pageDef);
        sharedLogger.debug(`   Resolved active version for page "${pageId}"`);
        if (activePageDef.id !== pageId) {
          sharedLogger.debug(`   Active version ID: "${activePageDef.id}" (original: "${pageId}")`);
        }
      } catch (error) {
        sharedLogger.warn(`[SEARCH DEBUG]   Failed to resolve version for page "${pageId}": ${error}`);
        continue;
      }
      if (activePageDef.showInSearch === false) {
        sharedLogger.debug(`   Skipping active version of page "${pageId}" - showInSearch is false`);
        continue;
      }
      let relevance = 0;
      let matchType = "";
      let matchDetails = [];
      if (activePageDef.title) {
        const titleLower = activePageDef.title.toLowerCase();
        const titleMatch = titleLower.includes(term);
        sharedLogger.debug(`   Title check: "${activePageDef.title}" -> ${titleMatch}`);
        if (titleMatch) {
          relevance += 10;
          matchType = "title";
          matchDetails.push(`title: "${activePageDef.title}"`);
          sharedLogger.debug(`   \u2713 Title match found! Relevance: ${relevance}`);
        }
      } else {
        sharedLogger.debug(`   Title check: No title defined`);
      }
      if (activePageDef.body) {
        const bodyLower = activePageDef.body.toLowerCase();
        const bodyMatch = bodyLower.includes(term);
        sharedLogger.debug(`   Body check: "${activePageDef.body.substring(0, 50)}${activePageDef.body.length > 50 ? "..." : ""}" -> ${bodyMatch}`);
        if (bodyMatch) {
          relevance += 5;
          if (!matchType)
            matchType = "body";
          matchDetails.push(`body: "${activePageDef.body.substring(0, 100)}${activePageDef.body.length > 100 ? "..." : ""}"`);
          sharedLogger.debug(`   \u2713 Body match found! Relevance: ${relevance}`);
        }
      } else {
        sharedLogger.debug(`   Body check: No body defined`);
      }
      if (activePageDef.buttons) {
        sharedLogger.debug(`   Button check: ${activePageDef.buttons.length} buttons`);
        for (let i = 0; i < activePageDef.buttons.length; i++) {
          const button = activePageDef.buttons[i];
          const buttonTextLower = button.text.toLowerCase();
          const buttonMatch = buttonTextLower.includes(term);
          sharedLogger.debug(`     Button ${i + 1}: "${button.text}" -> ${buttonMatch}`);
          if (buttonMatch) {
            relevance += 3;
            if (!matchType)
              matchType = "button";
            matchDetails.push(`button ${i + 1}: "${button.text}"`);
            sharedLogger.debug(`   \u2713 Button match found! Relevance: ${relevance}`);
            break;
          }
        }
      } else {
        sharedLogger.debug(`   Button check: No buttons defined`);
      }
      if (activePageDef.fields) {
        sharedLogger.debug(`   Field check: ${activePageDef.fields.length} fields`);
        for (let i = 0; i < activePageDef.fields.length; i++) {
          const field = activePageDef.fields[i];
          const fieldLabelLower = field.label.toLowerCase();
          const fieldMatch = fieldLabelLower.includes(term);
          sharedLogger.debug(`     Field ${i + 1}: "${field.label}" -> ${fieldMatch}`);
          if (fieldMatch) {
            relevance += 2;
            if (!matchType)
              matchType = "field";
            matchDetails.push(`field ${i + 1}: "${field.label}"`);
            sharedLogger.debug(`   \u2713 Field match found! Relevance: ${relevance}`);
            break;
          }
        }
      } else {
        sharedLogger.debug(`   Field check: No fields defined`);
      }
      if (relevance > 0) {
        pagesWithMatches++;
        sharedLogger.debug(`   \u2713 Page "${pageId}" has matches! Final relevance: ${relevance}, match type: ${matchType}`);
        sharedLogger.debug(`   Match details: ${matchDetails.join(", ")}`);
        let pageIcon;
        if (activePageDef.buttons) {
          for (const button of activePageDef.buttons) {
            if (button.icon) {
              pageIcon = button.icon;
              sharedLogger.debug(`   Using icon: ${pageIcon}`);
              break;
            }
          }
        }
        if (!pageIcon) {
          sharedLogger.debug(`   No icon found, will use default`);
        }
        const pageTitle = activePageDef.title && activePageDef.title.trim() ? activePageDef.title.trim() : pageId || "Untitled Page";
        results.push({
          pageId,
          // Use original pageId for navigation, not the versioned one
          title: pageTitle,
          relevance,
          matchType,
          icon: pageIcon
        });
      } else {
        sharedLogger.debug(`   \u2717 No matches found for page "${pageId}"`);
      }
    }
    sharedLogger.debug(` Search completed! Pages checked: ${pagesChecked}, pages with matches: ${pagesWithMatches}`);
    sharedLogger.debug(` Raw results before sorting: ${JSON.stringify(results.map((r) => ({ id: r.pageId, relevance: r.relevance, type: r.matchType })))}`);
    results.sort((a, b) => b.relevance - a.relevance);
    sharedLogger.debug(` Results after sorting: ${JSON.stringify(results.map((r) => ({ id: r.pageId, relevance: r.relevance, type: r.matchType })))}`);
    if (results.length === 0) {
      sharedLogger.warn(`[SEARCH DEBUG] No results found for search term: "${term}"`);
      Guidebook.showPopup(player, "Search Results", `No results found for "${searchTerm}"`);
      return;
    }
    sharedLogger.debug(` Creating search results page with ${results.length} results`);
    const searchResultsPageId = `search_results_${Date.now()}`;
    sharedLogger.debug(` Generated search results page ID: ${searchResultsPageId}`);
    const searchResultsPage = {
      id: searchResultsPageId,
      title: `Search Results for "${searchTerm}"`,
      body: `Found ${results.length} result(s):

${results.slice(0, 10).map((result, index) => {
        const resultTitle = result.title && result.title.trim() ? result.title : `Result ${index + 1}`;
        return `${index + 1}. ${resultTitle}\xA7r`;
      }).join("\n")}${results.length > 10 ? "\n\n... and " + (results.length - 10) + " more results" : ""}`,
      buttons: []
    };
    sharedLogger.debug(` Search results page body: ${searchResultsPage.body}`);
    const topResults = results.slice(0, 5);
    sharedLogger.debug(` Adding navigation buttons for top ${topResults.length} results`);
    topResults.forEach((result, index) => {
      const rawButtonText = result.title || `Page ${index + 1}`;
      const buttonText = rawButtonText.trim() || `Result ${index + 1}`;
      const buttonAction = `navigateTo:${result.pageId}`;
      const buttonIcon = result.icon || "textures/items/book_writable";
      sharedLogger.debug(`   Adding button ${index + 1}: "${rawButtonText}" -> "${buttonText}" -> ${buttonAction} (icon: ${buttonIcon})`);
      searchResultsPage.buttons.push({
        text: buttonText,
        action: buttonAction,
        icon: buttonIcon
      });
    });
    sharedLogger.debug(` Adding main button`);
    searchResultsPage.buttons.push({
      text: "Home",
      action: "navigateTo:main",
      icon: "textures/ui/home"
    });
    sharedLogger.debug(` Adding back button`);
    searchResultsPage.buttons.push({
      text: "Back",
      action: "back",
      icon: "textures/ui/arrow_left"
    });
    sharedLogger.debug(` Total buttons on search results page: ${searchResultsPage.buttons.length}`);
    sharedLogger.debug(` Adding temporary search results page to pageDefs`);
    this.guidebook.getPageDefs().set(searchResultsPageId, searchResultsPage);
    sharedLogger.debug(` PageDefs size after adding search page: ${this.guidebook.getPageDefs().size}`);
    sharedLogger.debug(` Navigating player to search results page`);
    this.guidebook.navigateTo(player, searchResultsPageId);
    sharedLogger.debug(` Scheduling cleanup of temporary search page in 100ms`);
    system12.runTimeout(() => {
      sharedLogger.debug(` Cleaning up temporary search page: ${searchResultsPageId}`);
      const wasDeleted = this.guidebook.getPageDefs().delete(searchResultsPageId);
      sharedLogger.debug(` Cleanup result: ${wasDeleted ? "success" : "failed"} (PageDefs size: ${this.guidebook.getPageDefs().size})`);
    }, 100);
    sharedLogger.debug(` Search process completed successfully for player ${player.name}`);
  }
  /**
   * Resolves the appropriate version of a page based on player properties.
   *
   * This method determines which version of a page should be shown to a player
   * based on the value of the page's version control property. If no version
   * matches the current property value, it falls back to a default version.
   *
   * @param player The player to resolve the version for
   * @param pageDef The page definition to resolve
   * @returns The resolved page definition
   * @throws Error if version resolution fails and no default is available
   *
   * @private
   *
   * @example
   * ```typescript
   * // This method is used internally by the search functionality
   * // to ensure the correct version of each page is searched
   * ```
   */
  _resolvePageVersion(player, pageDef) {
    if (!pageDef.versions) {
      return pageDef;
    }
    const versionControlProperty = pageDef.version_control_property;
    if (!versionControlProperty) {
      throw new Error(`Page ${pageDef.id} has versions defined without a version control property.`);
    }
    const vcpValue = this.guidebook.propertyManager.getProperty(player, versionControlProperty);
    let page = pageDef.versions.find((v) => v.value == vcpValue);
    if (!page) {
      sharedLogger.warn(`Unable to resolve version ${vcpValue} for versions on ${pageDef.id}. Defaulting to 'default'`);
      page = pageDef.versions.find((v) => v.value == 0);
    }
    if (!page) {
      throw new Error(`Unable to resolve version ${vcpValue} for versions on ${pageDef.id} and no default (value 'default') was found.`);
    }
    return {
      id: `${pageDef.id}.${page.value}`,
      ...page
    };
  }
};

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/DebugManager.js
var DebugManager = class {
  /**
   * Creates a new DebugManager instance.
   *
   * @param guidebook The parent guidebook instance
   *
   * @example
   * ```typescript
   * const debugManager = new DebugManager(guidebook);
   * ```
   */
  constructor(guidebook2) {
    this.guidebook = guidebook2;
  }
  /**
   * Sets up debug mode functionality.
   *
   * This method creates a debug page with various developer tools and registers
   * debug actions for inspecting the guidebook system state. The debug page
   * provides access to:
   * - List all pages and their IDs
   * - Check player state and navigation history
   * - Reset player state
   * - View system information and memory usage
   *
   * @example
   * ```typescript
   * // This is automatically called when debug mode is enabled
   * debugManager.setup();
   * ```
   */
  setup() {
    const debugPage = {
      id: "debug_info",
      title: "\xA76Debug Information",
      body: "Developer tools and system information for debugging the guidebook.",
      buttons: [
        { "text": "\xA7eList All Pages", "action": "debug:list_pages", "icon": "textures/items/compass_item" },
        { "text": "\xA7aCheck My State", "action": "debug:check_state", "icon": "textures/items/clock_item" },
        { "text": "\xA7cReset My State", "action": "debug:reset_state", "icon": "textures/items/barrier" },
        { "text": "\xA7bSystem Info", "action": "debug:system_info", "icon": "textures/items/book_writable" },
        { "text": "\xA77Back to Hub", "action": "back", "icon": "textures/ui/arrow_left" }
      ]
    };
    this.guidebook.getPageDefs().set("debug_info", debugPage);
    this.guidebook.registerAction("debug:list_pages", (player) => {
      const pageIds = this.guidebook.getPageIds();
      const actionNames = this.guidebook.getActionNames();
      const parserNames = this.guidebook.getTextParserNames();
      const debugInfo = [
        `\xA76=== Guidebook Debug Info ===`,
        `\xA7ePages (${pageIds.length}): \xA7f${pageIds.join(", ")}`,
        `\xA7eActions (${actionNames.length}): \xA7f${actionNames.join(", ")}`,
        `\xA7eText Parsers (${parserNames.length}): \xA7f${parserNames.join(", ")}`,
        `\xA7eDebug Mode: \xA7a${this.guidebook.isDebugMode() ? "Enabled" : "Disabled"}`,
        `\xA7eOpen Players: \xA7f${this.guidebook.getOpenPlayers().size}`,
        `\xA7eTotal Page Definitions: \xA7f${this.guidebook.getPageDefs().size}`
      ].join("\n");
      Guidebook.showPopup(player, "Debug: List Pages", debugInfo);
    });
    this.guidebook.registerAction("debug:check_state", (player) => {
      const state = this.guidebook.getPlayerState(player);
      const isOpen = this.guidebook.isOpen(player);
      const stateInfo = [
        `\xA76=== Player State Debug ===`,
        `\xA7ePlayer: \xA7f${player.name}`,
        `\xA7eGuidebook Open: \xA7f${isOpen ? "Yes" : "No"}`,
        `\xA7eCurrent Page: \xA7f${state.currentPage || "None"}`,
        `\xA7eNavigation Stack: \xA7f${state.navStack.join(" -> ") || "Empty"}`,
        `\xA7eLast Opened Page: \xA7f${this.guidebook.getLastOpenedPage(player) || "None"}`
      ].join("\n");
      Guidebook.showPopup(player, "Debug: Player State", stateInfo);
    });
    this.guidebook.registerAction("debug:reset_state", (player) => {
      this.guidebook.resetPlayerState(player);
      Guidebook.showPopup(player, "Debug: Reset State", `\xA7aReset guidebook state for ${player.name}`);
    });
    this.guidebook.registerAction("debug:system_info", (player) => {
      const systemInfo = [
        `\xA76=== System Information ===`,
        `\xA7eGuidebook Version: \xA7f1.0.0`,
        `\xA7eDebug Mode: \xA7a${this.guidebook.isDebugMode() ? "Enabled" : "Disabled"}`,
        `\xA7eTotal Pages: \xA7f${this.guidebook.getPageDefs().size}`,
        `\xA7eRegistered Actions: \xA7f${this.guidebook.getActions().size}`,
        `\xA7eText Parsers: \xA7f${this.guidebook.getTextParsers().size}`,
        `\xA7eOpen Players: \xA7f${this.guidebook.getOpenPlayers().size}`,
        `\xA7eComponent ID: \xA7f${this.guidebook.getComponentId()}`,
        `\xA7eMemory Usage: \xA7f${this._getMemoryUsage()}`
      ].join("\n");
      Guidebook.showPopup(player, "Debug: System Info", systemInfo);
    });
    sharedLogger.info("Debug mode setup complete. Debug page and actions registered.");
  }
  /**
   * Gets approximate memory usage for debug purposes.
   *
   * This method provides a rough estimate of the number of objects being tracked
   * by the guidebook system, which can be useful for debugging memory issues.
   *
   * @returns Memory usage string with object count
   *
   * @private
   *
   * @example
   * ```typescript
   * // This method is used internally by the system info debug action
   * const usage = this._getMemoryUsage();
   * // Returns something like "25 objects"
   * ```
   */
  _getMemoryUsage() {
    const pageCount = this.guidebook.getPageDefs().size;
    const actionCount = this.guidebook.getActions().size;
    const parserCount = this.guidebook.getTextParsers().size;
    const playerCount = this.guidebook.getOpenPlayers().size + this.guidebook.getPlayerNavStacks().size;
    return `${pageCount + actionCount + parserCount + playerCount} objects`;
  }
};

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/FormBuilder.js
import { GameMode, ItemStack as ItemStack6 } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
var FormBuilder = class {
  /**
   * Creates a new FormBuilder instance.
   *
   * @param guidebook The parent guidebook instance
   *
   * @example
   * ```typescript
   * const formBuilder = new FormBuilder(guidebook);
   * ```
   */
  constructor(guidebook2) {
    this.guidebook = guidebook2;
  }
  /**
   * Builds and shows an action form for a page.
   *
   * Action forms are used for pages that only have buttons (no input fields).
   * This method creates an ActionFormData instance, adds all the page buttons,
   * and handles the form response to execute the appropriate actions.
   *
   * @param player The player to show the form to
   * @param pageDef The page definition containing buttons and actions
   * @param title The parsed title text for the form
   * @param body The parsed body text for the form
   *
   * @example
   * ```typescript
   * // This method is called internally when displaying pages with buttons only
   * formBuilder.buildActionForm(player, pageDef, "Welcome", "Choose an option:");
   * ```
   */
  buildActionForm(player, pageDef, title, body) {
    sharedLogger.debug(` Building action form for page: "${pageDef.id}"`);
    sharedLogger.debug(` Title: "${title}"`);
    sharedLogger.debug(` Body: "${body}"`);
    sharedLogger.debug(` Page has ${pageDef.buttons?.length || 0} buttons`);
    const formTitle = title && title.trim() ? title : "Guidebook";
    sharedLogger.debug(` Using form title: "${formTitle}"`);
    let form;
    try {
      form = new ActionFormData().title(formTitle);
      sharedLogger.debug(` ActionFormData created successfully`);
    } catch (error) {
      sharedLogger.error(` Failed to create ActionFormData: ${error}`);
      this.guidebook.getOpenPlayers().delete(player.id);
      return;
    }
    if (body && body.trim()) {
      try {
        form.body(body);
        sharedLogger.debug(` Body added successfully: "${body}"`);
      } catch (error) {
        sharedLogger.error(` Failed to add body to form: ${error}`);
      }
    }
    const isCreative = player.getGameMode() === GameMode.Creative || player.getGameMode().toLowerCase() === "creative";
    const hasAssociatedItem = pageDef.associated_item;
    let hasGetItemButton = false;
    sharedLogger.debug(`Player is in creative mode: ${isCreative} and has associated item: ${hasAssociatedItem}`);
    if (isCreative && hasAssociatedItem) {
      try {
        form.button("Get Item", "textures/ui/gift_square");
        hasGetItemButton = true;
        sharedLogger.debug(`Added "Get Item" button for ${pageDef.associated_item}`);
      } catch (error) {
        sharedLogger.error(` Failed to add "Get Item" button: ${error}`);
      }
    }
    pageDef.buttons?.forEach((button, index) => {
      try {
        const parsedText = this.guidebook.propertyManager.parseText(player, button.text);
        sharedLogger.debug(`   Adding button ${index + 1}: "${button.text}" -> "${parsedText}" (icon: ${button.icon || "none"})`);
        const buttonText = parsedText && parsedText.trim() ? parsedText : `Button ${index + 1}`;
        const buttonIcon = button.icon || void 0;
        form.button(buttonText, buttonIcon);
        sharedLogger.debug(`   Button ${index + 1} added successfully`);
      } catch (error) {
        sharedLogger.error(`   Failed to add button ${index + 1}: ${error}`);
        sharedLogger.error(`   Button data: text="${button.text}", icon="${button.icon}"`);
      }
    });
    sharedLogger.debug(` Attempting to show action form to player ${player.name}`);
    try {
      form.show(player).then((response) => {
        sharedLogger.debug(` Action form response received from ${player.name}: ${JSON.stringify(response)}`);
        this.guidebook.eventManager.triggerCloseEventsAndHooks(player, pageDef);
        if (response.canceled) {
          this._handleAction(player, "close");
          return;
        }
        if (hasGetItemButton && response.selection === 0) {
          this._handleAction(player, `give_item:${pageDef.associated_item}`);
        } else {
          const buttonIndex = hasGetItemButton ? response.selection - 1 : response.selection;
          const selectedButton = pageDef.buttons?.[buttonIndex];
          if (selectedButton) {
            this._handleAction(player, selectedButton.action);
            return;
          }
        }
      }).catch((error) => {
        sharedLogger.error(`Error showing action form: ${error}`);
        sharedLogger.error(`Page ID: ${pageDef.id}, Title: "${formTitle}", Body: "${body}"`);
        sharedLogger.error(`Button count: ${pageDef.buttons?.length || 0}, Has Get Item: ${hasGetItemButton}`);
        if (pageDef.buttons) {
          pageDef.buttons.forEach((btn, idx) => {
            sharedLogger.error(`  Button ${idx}: "${btn.text}" (icon: ${btn.icon || "none"})`);
          });
        }
        this.guidebook.getOpenPlayers().delete(player.id);
      });
    } catch (syncError) {
      sharedLogger.error(`Synchronous error creating action form: ${syncError}`);
      sharedLogger.error(`Page ID: ${pageDef.id}, Title: "${formTitle}", Body: "${body}"`);
      this.guidebook.getOpenPlayers().delete(player.id);
    }
  }
  /**
   * Builds and shows a modal form for a page with fields.
   *
   * Modal forms are used for pages that have input fields (text fields, toggles,
   * sliders, dropdowns). This method creates a ModalFormData instance, adds all
   * the page fields with their current values, and handles form submission to
   * save the field values and execute the submit action.
   *
   * @param player The player to show the form to
   * @param pageDef The page definition containing fields and submit action
   * @param title The parsed title text for the form
   * @param body The parsed body text for the form
   *
   * @example
   * ```typescript
   * // This method is called internally when displaying pages with input fields
   * formBuilder.buildModalForm(player, pageDef, "Settings", "Configure your preferences:");
   * ```
   */
  buildModalForm(player, pageDef, title, body) {
    sharedLogger.debug(` Building modal form for page: "${pageDef.id}"`);
    sharedLogger.debug(` Title: "${title}"`);
    sharedLogger.debug(` Body: "${body}"`);
    sharedLogger.debug(` Page has on_submit_action: "${pageDef.on_submit_action}"`);
    sharedLogger.debug(` Page has ${pageDef.fields?.length || 0} fields`);
    const formTitle = title && title.trim() ? title : "Guidebook";
    const form = new ModalFormData().title(formTitle);
    pageDef.fields?.forEach((field, index) => {
      sharedLogger.debug(` Processing field ${index + 1}: type="${field.type}", label="${field.label}"`);
      const label = this.guidebook.propertyManager.parseText(player, field.label);
      const propValue = this.guidebook.propertyManager.getProperty(player, field.property) ?? field.default;
      sharedLogger.debug(`   Parsed label: "${label}"`);
      sharedLogger.debug(`   Property value: ${JSON.stringify(propValue)}`);
      switch (field.type) {
        case "toggle":
          sharedLogger.debug(`   Adding toggle field`);
          try {
            const toggleValue = propValue !== null && propValue !== void 0 ? !!propValue : !!field.default;
            sharedLogger.debug(`   Toggle value: ${toggleValue} (from: ${JSON.stringify(propValue)})`);
            try {
              const toggleOptions = {
                defaultValue: toggleValue
              };
              if (field.tooltip && field.tooltip.trim()) {
                toggleOptions.tooltip = field.tooltip;
              }
              form.toggle(label, toggleOptions);
              sharedLogger.debug(`   Toggle field added with new API`);
            } catch (newApiError) {
              sharedLogger.debug(`   New API failed, trying old API: ${newApiError}`);
              try {
                form.toggle(label, toggleValue);
                sharedLogger.debug(`   Toggle field added with old API`);
              } catch (oldApiError) {
                sharedLogger.debug(`   Old API also failed, trying minimal: ${oldApiError}`);
                form.toggle(label);
              }
            }
          } catch (error) {
            sharedLogger.error(`   Failed to add toggle field with all APIs: ${error}`);
          }
          break;
        case "slider":
          {
            sharedLogger.debug(`   Adding slider field`);
            try {
              const typedField = field;
              let sliderValue = Number(propValue);
              if (isNaN(sliderValue) || propValue === null || propValue === void 0) {
                sliderValue = Number(typedField.default) || typedField.min || 0;
              }
              sliderValue = Math.max(typedField.min, Math.min(typedField.max, sliderValue));
              sharedLogger.debug(`   Slider value: ${sliderValue} (from: ${JSON.stringify(propValue)})`);
              try {
                const sliderOptions = {
                  defaultValue: sliderValue,
                  valueStep: typedField.step || 1
                };
                if (typedField.tooltip && typedField.tooltip.trim()) {
                  sliderOptions.tooltip = typedField.tooltip;
                }
                form.slider(label, typedField.min, typedField.max, sliderOptions);
                sharedLogger.debug(`   Slider field added with new API`);
              } catch (newApiError) {
                sharedLogger.debug(`   New API failed, trying old API: ${newApiError}`);
                try {
                  form.slider(label, typedField.min, typedField.max, typedField.step || 1, sliderValue);
                  sharedLogger.debug(`   Slider field added with old API`);
                } catch (oldApiError) {
                  sharedLogger.debug(`   Old API also failed, trying minimal: ${oldApiError}`);
                  form.slider(label, typedField.min, typedField.max, 1);
                }
              }
            } catch (error) {
              sharedLogger.error(`   Failed to add slider field: ${error}`);
              const typedField = field;
              form.slider(label, typedField.min || 0, typedField.max || 100, { defaultValue: typedField.min || 0 });
            }
          }
          break;
        case "dropdown":
          sharedLogger.debug(`   Adding dropdown field`);
          try {
            const dropdownField = field;
            const options = dropdownField.options.map((o) => this.guidebook.propertyManager.parseText(player, o));
            let selectedIndex = Number(propValue);
            if (isNaN(selectedIndex) || propValue === null || propValue === void 0) {
              selectedIndex = Number(dropdownField.default) || 0;
            }
            selectedIndex = Math.max(0, Math.min(options.length - 1, selectedIndex));
            sharedLogger.debug(`   Dropdown index: ${selectedIndex} (from: ${JSON.stringify(propValue)}, options: ${options.length})`);
            try {
              const dropdownOptions = {
                defaultValueIndex: selectedIndex
              };
              if (dropdownField.tooltip && dropdownField.tooltip.trim()) {
                dropdownOptions.tooltip = dropdownField.tooltip;
              }
              form.dropdown(label, options, dropdownOptions);
              sharedLogger.debug(`   Dropdown field added with new API`);
            } catch (newApiError) {
              sharedLogger.debug(`   New API failed, trying old API: ${newApiError}`);
              try {
                form.dropdown(label, options, selectedIndex);
                sharedLogger.debug(`   Dropdown field added with old API`);
              } catch (oldApiError) {
                sharedLogger.debug(`   Old API also failed, trying minimal: ${oldApiError}`);
                form.dropdown(label, options);
              }
            }
          } catch (error) {
            sharedLogger.error(`   Failed to add dropdown field: ${error}`);
            form.dropdown(label, ["Option 1"], { defaultValueIndex: 0 });
          }
          break;
        case "textField":
          sharedLogger.debug(`   Adding text field`);
          try {
            const textField = field;
            const parsedPlaceholder = this.guidebook.propertyManager.parseText(player, textField.placeholder ?? "");
            sharedLogger.debug(`   Placeholder: "${textField.placeholder}" -> "${parsedPlaceholder}"`);
            const textValue = propValue !== null && propValue !== void 0 ? String(propValue) : textField.default || "";
            sharedLogger.debug(`   Text value: "${textValue}" (from: ${JSON.stringify(propValue)})`);
            try {
              const textOptions = {
                defaultValue: textValue
              };
              if (textField.tooltip && textField.tooltip.trim()) {
                textOptions.tooltip = textField.tooltip;
              }
              form.textField(label, parsedPlaceholder || "Enter text...", textOptions);
              sharedLogger.debug(`   Text field added with new API`);
            } catch (newApiError) {
              sharedLogger.debug(`   New API failed, trying old API: ${newApiError}`);
              try {
                form.textField(label, parsedPlaceholder || "Enter text...", textValue);
                sharedLogger.debug(`   Text field added with old API`);
              } catch (oldApiError) {
                sharedLogger.debug(`   Old API also failed, trying minimal: ${oldApiError}`);
                form.textField(label, parsedPlaceholder || "Enter text...");
              }
            }
          } catch (error) {
            sharedLogger.error(`   Failed to add text field: ${error}`);
            form.textField(label, "Enter text...", { defaultValue: "" });
          }
          break;
      }
    });
    sharedLogger.debug(` Showing modal form to player ${player.name}`);
    form.show(player).then((response) => {
      this.guidebook.eventManager.triggerCloseEventsAndHooks(player, pageDef);
      if (response.canceled) {
        this._handleAction(player, "close");
        return;
      }
      response.formValues?.forEach((value, index) => {
        const field = pageDef.fields?.[index];
        if (!field)
          return;
        this.guidebook.propertyManager.setProperty(player, field.property, value);
        if (field.type === "toggle" && value === true && field.set_properties) {
          field.set_properties.forEach((reset) => {
            this.guidebook.propertyManager.setProperty(player, reset.property, reset.value);
          });
          this.guidebook.propertyManager.setProperty(player, field.property, false);
        }
      });
      if (pageDef.on_submit_action) {
        sharedLogger.debug(` Form submitted with on_submit_action: "${pageDef.on_submit_action}"`);
        sharedLogger.debug(` Form response: ${JSON.stringify(response)}`);
        sharedLogger.debug(` Form values: ${JSON.stringify(response.formValues)}`);
        const action = this.guidebook.getActions().get(pageDef.on_submit_action);
        if (action) {
          sharedLogger.debug(` Found registered action: ${pageDef.on_submit_action}`);
          action(player, response.formValues);
        } else if (pageDef.on_submit_action === "search") {
          sharedLogger.debug(` Handling built-in search action`);
          this._handleAction(player, "search", response.formValues);
          return;
        } else {
          sharedLogger.warn(`[SEARCH DEBUG] Couldn't find action ${pageDef.on_submit_action}`);
        }
      }
      this._handleAction(player, "back");
    }).catch((error) => {
      sharedLogger.error(`Error showing modal form: ${error}`);
      sharedLogger.error(`Modal Form Details - Page ID: ${pageDef.id}, Title: "${formTitle}", Fields: ${pageDef.fields?.length || 0}`);
      if (pageDef.fields) {
        pageDef.fields.forEach((field, idx) => {
          sharedLogger.error(`  Field ${idx}: type="${field.type}", label="${field.label}"`);
        });
      }
      this.guidebook.getOpenPlayers().delete(player.id);
    });
  }
  /**
   * Handles action execution for form responses and button clicks.
   *
   * This method processes various types of actions including:
   * - Navigation actions (navigateTo:, back, close)
   * - Built-in actions (search)
   * - Custom registered actions
   * - Object-based actions (set_properties)
   * - Array of multiple actions
   *
   * @param player The player who triggered the action
   * @param action The action(s) to execute (string, object, or array)
   * @param formValues Optional form values from modal form submission
   *
   * @private
   *
   * @example
   * ```typescript
   * // This method is called internally to handle button clicks and form submissions
   * this._handleAction(player, "navigateTo:next_page");
   * this._handleAction(player, "search", ["tutorial"]);
   * ```
   */
  _handleAction(player, action, formValues) {
    if (!action)
      return;
    if (Array.isArray(action)) {
      action.forEach((singleAction) => this._handleAction(player, singleAction, formValues));
      return;
    }
    if (typeof action === "object") {
      if (action.action === "set_properties") {
        action.properties.forEach((propInfo) => {
          this.guidebook.propertyManager.setProperty(player, propInfo.property, propInfo.value);
        });
      }
      return;
    }
    const navStack = this.guidebook.getPlayerNavStacks().get(player.id) || [];
    if (action.startsWith("navigateTo:")) {
      const pageId = action.substring(11);
      this.guidebook.navigateTo(player, pageId);
    } else if (action === "back") {
      navStack.pop();
      const previousPage = navStack.pop();
      this.guidebook.navigateTo(player, previousPage || "main");
    } else if (action === "close") {
      this.guidebook.setLastOpenedPage(player, navStack[navStack.length - 1]);
      this.guidebook.getPlayerNavStacks().delete(player.id);
      this.guidebook.getOpenPlayers().delete(player.id);
    } else if (action === "search" && formValues && formValues.length > 0) {
      sharedLogger.debug(` Search action triggered by ${player.name}`);
      sharedLogger.debug(` Form values received: ${JSON.stringify(formValues)}`);
      sharedLogger.debug(` Form values length: ${formValues.length}`);
      sharedLogger.debug(` First form value: "${formValues[0]}" (type: ${typeof formValues[0]})`);
      this.guidebook.pageManager.performSearch(player, formValues[0]);
    } else if (action === "search") {
      sharedLogger.warn(`[SEARCH DEBUG] Search action triggered but no form values provided`);
      sharedLogger.warn(`[SEARCH DEBUG] Form values: ${JSON.stringify(formValues)}`);
    } else if (action.startsWith("give_item:")) {
      const itemId = action.substring(10);
      this._giveItemToPlayer(player, itemId);
    } else if (this.guidebook.getActions().has(action)) {
      this.guidebook.getActions().get(action)(player, formValues);
    } else {
      sharedLogger.warn(`Unhandled action: ${action}`);
    }
  }
  /**
   * Gives an item to a player in their inventory.
   *
   * This method attempts to give the specified item to the player and provides
   * feedback about the success or failure of the operation.
   *
   * @param player The player to give the item to
   * @param itemId The item identifier (e.g., "minecraft:diamond", "minecraft:iron_sword")
   *
   * @private
   */
  _giveItemToPlayer(player, itemId) {
    try {
      const itemStack = new ItemStack6(itemId, 1);
      const inventory = player.getComponent("minecraft:inventory");
      if (inventory && inventory.container) {
        try {
          inventory.container.addItem(itemStack);
          sharedLogger.info(`Gave ${itemId} to ${player.name}`);
          player.sendMessage(`\xA7aReceived: ${itemId.replace("minecraft:", "")}`);
        } catch (error) {
          sharedLogger.info(`Failed to give ${itemId} to ${player.name} - inventory might be full`);
          player.sendMessage("\xA7cInventory is full!");
        }
      } else {
        sharedLogger.error(`Failed to access inventory for player ${player.name}`);
        player.sendMessage("\xA7cFailed to give item - inventory not accessible");
      }
    } catch (error) {
      sharedLogger.error(`Error giving item ${itemId} to ${player.name}: ${error}`);
      player.sendMessage("\xA7cFailed to give item - invalid item ID or other error");
    }
  }
};

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/EventManager.js
import { system as system13, world as world11 } from "@minecraft/server";
var EventManager = class {
  /**
   * Creates a new EventManager instance.
   *
   * @param guidebook The parent guidebook instance
   *
   * @example
   * ```typescript
   * const eventManager = new EventManager(guidebook);
   * ```
   */
  constructor(guidebook2) {
    this.pageOpenHooks = /* @__PURE__ */ new Map();
    this.pageFirstOpenHooks = /* @__PURE__ */ new Map();
    this.pageCloseHooks = /* @__PURE__ */ new Map();
    this.guidebook = guidebook2;
  }
  /**
   * Registers a callback for when a page opens.
   *
   * This callback will be triggered every time the specified page is opened.
   * Use "*" as the pageId to register a callback for all pages.
   *
   * @param pageId The page ID to register the callback for, or "*" for all pages
   * @param callback The function to execute when the page opens
   * @returns The parent guidebook instance for chaining
   *
   * @example
   * ```typescript
   * guidebook.eventManager.onPageOpen("tutorial", (player, pageId) => {
   *   console.log(`${player.name} opened ${pageId}`);
   * });
   *
   * // Register for all pages
   * guidebook.eventManager.onPageOpen("*", (player, pageId) => {
   *   console.log(`Page ${pageId} was opened`);
   * });
   * ```
   */
  onPageOpen(pageId, callback) {
    if (!this.pageOpenHooks.has(pageId))
      this.pageOpenHooks.set(pageId, []);
    this.pageOpenHooks.get(pageId)?.push(callback);
    return this.guidebook;
  }
  /**
   * Registers a callback for when a page is opened for the first time.
   *
   * This callback will only be triggered the first time a player opens the specified page.
   * The system tracks this using world dynamic properties.
   *
   * @param pageId The page ID to register the callback for, or "*" for all pages
   * @param callback The function to execute when the page is first opened
   * @returns The parent guidebook instance for chaining
   *
   * @example
   * ```typescript
   * guidebook.eventManager.onFirstPageOpen("welcome", (player, pageId) => {
   *   console.log(`${player.name} opened ${pageId} for the first time`);
   *   // Give them a welcome gift
   *   player.runCommand("give @s diamond 1");
   * });
   * ```
   */
  onFirstPageOpen(pageId, callback) {
    if (!this.pageFirstOpenHooks.has(pageId))
      this.pageFirstOpenHooks.set(pageId, []);
    this.pageFirstOpenHooks.get(pageId)?.push(callback);
    return this.guidebook;
  }
  /**
   * Registers a callback for when a page closes.
   *
   * This callback will be triggered when a player closes or navigates away from
   * the specified page. Use "*" as the pageId to register a callback for all pages.
   *
   * @param pageId The page ID to register the callback for, or "*" for all pages
   * @param callback The function to execute when the page closes
   * @returns The parent guidebook instance for chaining
   *
   * @example
   * ```typescript
   * guidebook.eventManager.onPageClose("settings", (player, pageId) => {
   *   console.log(`${player.name} closed ${pageId}`);
   *   // Save settings to database
   *   savePlayerSettings(player);
   * });
   * ```
   */
  onPageClose(pageId, callback) {
    if (!this.pageCloseHooks.has(pageId)) {
      this.pageCloseHooks.set(pageId, []);
    }
    this.pageCloseHooks.get(pageId)?.push(callback);
    return this.guidebook;
  }
  /**
   * Handles page events (on_open, on_close, on_first_open) defined in JSON.
   *
   * This method processes the events array defined in page configurations and
   * executes the appropriate actions (set_property, increment_property, etc.).
   * It also triggers any registered lifecycle callbacks.
   *
   * @param eventType The type of event to handle
   * @param pageDef The page definition containing the events
   * @param player The player involved in the event
   *
   * @example
   * ```typescript
   * // This method is called internally when pages are opened/closed
   * eventManager.handlePageEvents("on_open", pageDef, player);
   * ```
   */
  handlePageEvents(eventType, pageDef, player) {
    const events = pageDef[eventType];
    if (!events)
      return;
    if (eventType === "on_first_open") {
      const trackingProp = `guide:p:${player.id}:${pageDef.id}:opened`;
      if (world11.getDynamicProperty(trackingProp))
        return;
      world11.setDynamicProperty(trackingProp, true);
      this.pageFirstOpenHooks.get("*")?.forEach((hook) => hook(player));
      this.pageFirstOpenHooks.get(pageDef.id)?.forEach((hook) => hook(player));
      this.pageOpenHooks.get("*")?.forEach((hook) => hook(player));
      this.pageOpenHooks.get(pageDef.id)?.forEach((hook) => hook(player));
    }
    for (const event of events) {
      switch (event.action) {
        case "set_property":
          if (event.property) {
            this.guidebook.propertyManager.setProperty(player, event.property, event.value);
          }
          break;
        case "increment_property": {
          if (!event.property)
            break;
          const currentVal = Number(this.guidebook.propertyManager.getProperty(player, event.property) ?? 0);
          this.guidebook.propertyManager.setProperty(player, event.property, currentVal + (Number(event.value) || 1));
          break;
        }
        case "decrement_property": {
          if (!event.property)
            break;
          const currentVal = Number(this.guidebook.propertyManager.getProperty(player, event.property) ?? 0);
          this.guidebook.propertyManager.setProperty(player, event.property, currentVal - (Number(event.value) || 1));
          break;
        }
        case "trigger_script_event":
          if (event.script_event_id) {
            system13.sendScriptEvent(event.script_event_id, event.message ?? "");
          }
          break;
      }
    }
  }
  /**
   * Triggers close events and hooks for a page.
   *
   * This method is called when a page is closed or when a player navigates away.
   * It handles both the JSON-defined on_close events and any registered close callbacks.
   *
   * @param player The player closing the page
   * @param pageDef The page definition being closed
   *
   * @example
   * ```typescript
   * // This method is called internally when forms are submitted or canceled
   * eventManager.triggerCloseEventsAndHooks(player, pageDef);
   * ```
   */
  triggerCloseEventsAndHooks(player, pageDef) {
    const resolvedPageDef = this._resolvePageVersion(player, pageDef);
    this.handlePageEvents("on_close", resolvedPageDef, player);
    this.pageCloseHooks.get("*")?.forEach((hook) => hook(player));
    this.pageCloseHooks.get(resolvedPageDef.id)?.forEach((hook) => hook(player));
    this.guidebook.setLastOpenedPage(player, resolvedPageDef.id);
  }
  /**
   * Resolves page version for event handling.
   *
   * This method determines which version of a page should be used for event
   * processing based on the player's version control property value.
   *
   * @param player The player to resolve the version for
   * @param pageDef The page definition to resolve
   * @returns The resolved page definition
   * @throws Error if version resolution fails and no default is available
   *
   * @private
   *
   * @example
   * ```typescript
   * // This method is used internally to ensure events are processed
   * // for the correct version of a page
   * ```
   */
  _resolvePageVersion(player, pageDef) {
    if (!pageDef.versions) {
      return pageDef;
    }
    const versionControlProperty = pageDef.version_control_property;
    if (!versionControlProperty) {
      throw new Error(`Page ${pageDef.id} has versions defined without a version control property.`);
    }
    const vcpValue = this.guidebook.propertyManager.getProperty(player, versionControlProperty);
    let page = pageDef.versions.find((v) => {
      if (v.value == vcpValue)
        return v;
    });
    if (!page) {
      sharedLogger.warn(`Unable to resolve version ${vcpValue} for versions on ${pageDef.id}. Defaulting to 'default'`);
      page = pageDef.versions.find((v) => {
        if (v.value == 0)
          return v;
      });
    }
    if (!page) {
      throw new Error(`Unable to resolve version ${vcpValue} for versions on ${pageDef.id} and no default (value 'default') was found.`);
    }
    return {
      id: `${pageDef.id}.${page.value}`,
      ...page
    };
  }
  // --- Getters for hooks ---
  /**
   * Gets the map of page open hooks.
   *
   * @returns Map of page open callbacks by page ID
   *
   * @example
   * ```typescript
   * const openHooks = eventManager.getPageOpenHooks();
   * console.log(`Registered open hooks: ${openHooks.size}`);
   * ```
   */
  getPageOpenHooks() {
    return this.pageOpenHooks;
  }
  /**
   * Gets the map of first page open hooks.
   *
   * @returns Map of first page open callbacks by page ID
   *
   * @example
   * ```typescript
   * const firstOpenHooks = eventManager.getPageFirstOpenHooks();
   * console.log(`Registered first open hooks: ${firstOpenHooks.size}`);
   * ```
   */
  getPageFirstOpenHooks() {
    return this.pageFirstOpenHooks;
  }
  /**
   * Gets the map of page close hooks.
   *
   * @returns Map of page close callbacks by page ID
   *
   * @example
   * ```typescript
   * const closeHooks = eventManager.getPageCloseHooks();
   * console.log(`Registered close hooks: ${closeHooks.size}`);
   * ```
   */
  getPageCloseHooks() {
    return this.pageCloseHooks;
  }
};

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/PropertyManager.js
import { world as world12 } from "@minecraft/server";
var PropertyManager = class {
  /**
   * Creates a new PropertyManager instance.
   *
   * @param guidebook The parent guidebook instance
   *
   * @example
   * ```typescript
   * const propertyManager = new PropertyManager(guidebook);
   * ```
   */
  constructor(guidebook2) {
    this.guidebook = guidebook2;
  }
  /**
   * Gets a constant value for a player.
   *
   * This method returns predefined player constants that cannot be changed.
   *
   * Available constants:
   * - `player_name`: The player's display name
   * - `player_id`: The player's unique identifier
   *
   * @param player The player to get the constant for
   * @param constantName The name of the constant to retrieve
   * @returns The constant value or undefined if not found
   *
   * @example
   * ```typescript
   * // Get player name constant
   * const playerName = propertyManager.getConstant(player, "player_name");
   * // Returns the player's actual name
   * ```
   */
  getConstant(player, constantName) {
    switch (constantName) {
      case "player_name":
        return player.name;
      case "player_id":
        return player.id;
      case "player_gamemode":
        return player.getGameMode();
      case "player_level":
        return player.level;
      case "player_xp":
        return player.getTotalXp();
      case "player_dimension":
        return player.dimension;
      case "player_location":
        return player.location;
      default:
        sharedLogger.warn(`Unknown constant: ${constantName}`);
        return void 0;
    }
  }
  /**
   * Parses text with property placeholders.
   *
   * This method replaces property placeholders in text with their actual values.
   * It supports both dynamic properties and custom text parsers.
   *
   * Placeholder syntax:
   * - `{{p:property_name}}` - Player-scoped property
   * - `{{w:property_name}}` - World-scoped property
   * - `{{c:constant_name}}` - Player constant (read-only)
   * - `{{p:property_name|default_value}}` - Property with default value
   * - `{{parser:name}}` - Custom text parser
   *
   * @param player The player to parse text for
   * @param text The text containing placeholders to parse
   * @returns The parsed text with placeholders replaced
   *
   * @example
   * ```typescript
   * // Parse text with property placeholders
   * const parsed = propertyManager.parseText(player, "Hello {{p:player_name|Player}}!");
   * // Returns "Hello John!" if player_name property is "John"
   * // Returns "Hello Player!" if player_name property is not set
   *
   * // Parse text with constant
   * const parsed = propertyManager.parseText(player, "Hello {{c:player_name}}!");
   * // Returns "Hello Steve!" if player's actual name is "Steve"
   *
   * // Parse text with custom parser
   * const parsed = propertyManager.parseText(player, "Current time: {{parser:current_time}}");
   * // Returns "Current time: 14:30" if current_time parser returns "14:30"
   * ```
   */
  parseText(player, text) {
    if (!text) {
      sharedLogger.warn(`parseText called with null/undefined text`);
      return "";
    }
    sharedLogger.debug(`Parsing text: "${text}"`);
    const result = text.replace(/{{(.*?)}}/g, (match, expr) => {
      const [scope, name] = expr.split(":");
      if (!name)
        return match;
      if (this.guidebook.getTextParsers().has(name)) {
        sharedLogger.debug(`Found ${name} in textparsers.`);
        return String(this.guidebook.getTextParsers().get(name)(player));
      }
      if (scope === "c" || scope === "const") {
        const constantValue = this.getConstant(player, name);
        return constantValue !== void 0 ? String(constantValue) : match;
      }
      const propDef = {
        name: name.split("|")[0],
        defaultValue: name.split("|")[1],
        scope: scope === "p" ? "player" : "world"
      };
      return this.getProperty(player, propDef) ?? match;
    });
    sharedLogger.debug(`Parse result: "${result}"`);
    return result;
  }
  /**
   * Gets a property value for a player.
   *
   * This method retrieves the value of a dynamic property, either from the player
   * or from the world, depending on the property scope. If the property is not set,
   * it returns the default value specified in the property definition.
   *
   * @param player The player to get the property for
   * @param prop The property definition containing name, scope, and default value
   * @returns The property value or default value if not set
   *
   * @example
   * ```typescript
   * // Get a player-scoped property
   * const playerName = propertyManager.getProperty(player, {
   *   name: "player_name",
   *   scope: "player",
   *   defaultValue: "Unknown"
   * });
   *
   * // Get a world-scoped property
   * const serverName = propertyManager.getProperty(player, {
   *   name: "server_name",
   *   scope: "world",
   *   defaultValue: "My Server"
   * });
   * ```
   */
  getProperty(player, prop) {
    sharedLogger.debug(`Attempting to get ${prop.name} dynamic property in the ${prop.scope} scope`);
    try {
      const value = prop.scope === "player" ? player.getDynamicProperty(prop.name) : world12.getDynamicProperty(prop.name);
      sharedLogger.debug(`Got ${value} for ${prop.name}`);
      if (!value)
        return prop.defaultValue;
      else
        return value;
    } catch (error) {
      sharedLogger.error(`_getProperty failed with error ${error}. Returning default value ${prop.defaultValue} for ${prop.name}`);
      return prop.defaultValue;
    }
  }
  /**
   * Sets a property value for a player.
   *
   * This method stores a value in a dynamic property, either on the player
   * or on the world, depending on the property scope.
   *
   * @param player The player to set the property for (used for player-scoped properties)
   * @param prop The property definition containing name and scope
   * @param value The value to store in the property
   *
   * @example
   * ```typescript
   * // Set a player-scoped property
   * propertyManager.setProperty(player, {
   *   name: "tutorial_completed",
   *   scope: "player"
   * }, "true");
   *
   * // Set a world-scoped property
   * propertyManager.setProperty(player, {
   *   name: "server_version",
   *   scope: "world"
   * }, "1.0.0");
   * ```
   */
  setProperty(player, prop, value) {
    if (prop.scope === "player" && player) {
      player.setDynamicProperty(prop.name, value);
    } else if (prop.scope === "world") {
      world12.setDynamicProperty(prop.name, value);
    } else {
      sharedLogger.warn(`Attempted to set property ${prop.name} with scope ${prop.scope} but no player was provided`);
    }
  }
};

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/ItemManager.js
import { Player as Player6, system as system14, world as world13 } from "@minecraft/server";
var ItemManager = class {
  constructor(guidebookInstance, componentId = "guide:is_guidebook") {
    this.onBeforeDurabilityDamageHooks = [];
    this.onCompleteUseHooks = [];
    this.onConsumeHooks = [];
    this.onHitEntityHooks = [];
    this.onMineBlockHooks = [];
    this.onUseHooks = [];
    this.onUseOnHooks = [];
    this.isRegistered = false;
    this.guidebookInstance = guidebookInstance;
    this.componentId = componentId;
    sharedLogger.debug(`ItemManager initialized with component ID: ${componentId}`);
  }
  /**
   * Finds a page that is associated with a specific block.
   *
   * @param blockId The block identifier to search for
   * @returns The page ID associated with the block, or undefined if not found
   */
  findPageByAssociatedBlock(blockId) {
    if (!this.guidebookInstance) {
      sharedLogger.warn("Guidebook instance not available for block association lookup");
      return void 0;
    }
    const pageDefs = this.guidebookInstance.getPageDefs();
    for (const [pageId, pageDef] of pageDefs) {
      if (pageDef.associated_block === blockId) {
        sharedLogger.debug(`Found page "${pageId}" associated with block "${blockId}"`);
        return pageId;
      }
    }
    sharedLogger.debug(`No page found associated with block "${blockId}"`);
    return void 0;
  }
  onBeforeDurabilityDamage(callback) {
    this.onBeforeDurabilityDamageHooks.push(callback);
    sharedLogger.debug(`Added onBeforeDurabilityDamage hook: ${callback.name || "anonymous"}`);
    return this;
  }
  onCompleteUse(callback) {
    this.onCompleteUseHooks.push(callback);
    sharedLogger.debug(`Added onCompleteUse hook: ${callback.name || "anonymous"}`);
    return this;
  }
  onConsume(callback) {
    this.onConsumeHooks.push(callback);
    sharedLogger.debug(`Added onConsume hook: ${callback.name || "anonymous"}`);
    return this;
  }
  onHitEntity(callback) {
    this.onHitEntityHooks.push(callback);
    sharedLogger.debug(`Added onHitEntity hook: ${callback.name || "anonymous"}`);
    return this;
  }
  onMineBlock(callback) {
    this.onMineBlockHooks.push(callback);
    sharedLogger.debug(`Added onMineBlock hook: ${callback.name || "anonymous"}`);
    return this;
  }
  onUse(callback) {
    this.onUseHooks.push(callback);
    sharedLogger.debug(`Added onUse hook: ${callback.name || "anonymous"}`);
    return this;
  }
  onUseOn(callback) {
    this.onUseOnHooks.push(callback);
    sharedLogger.debug(`Added onUseOn hook: ${callback.name || "anonymous"}`);
    return this;
  }
  getComponentId() {
    return this.componentId;
  }
  isComponentRegistered() {
    return this.isRegistered;
  }
  registerComponent() {
    if (this.isRegistered) {
      sharedLogger.warn("Item component already registered");
      return this;
    }
    if (!this.guidebookInstance) {
      sharedLogger.error("Cannot register component: guidebook instance not initialized. Call init() first.");
      return this;
    }
    const onStartup = (event) => {
      const component = {
        onBeforeDurabilityDamage: async (e) => {
          if (!this.guidebookInstance)
            return;
          for (const hook of this.onBeforeDurabilityDamageHooks) {
            try {
              const result = await hook(e, this.guidebookInstance);
              if (result === false) {
                return;
              }
            } catch (err) {
              sharedLogger.error(`Error in onBeforeDurabilityDamage hook: ${err}`);
            }
          }
        },
        onCompleteUse: async (e) => {
          if (!this.guidebookInstance)
            return;
          for (const hook of this.onCompleteUseHooks) {
            try {
              const result = await hook(e, this.guidebookInstance);
              if (result === false) {
                return;
              }
            } catch (err) {
              sharedLogger.error(`Error in onCompleteUse hook: ${err}`);
            }
          }
        },
        onHitEntity: async (e) => {
          if (!this.guidebookInstance)
            return;
          for (const hook of this.onHitEntityHooks) {
            try {
              const result = await hook(e, this.guidebookInstance);
              if (result === false) {
                return;
              }
            } catch (err) {
              sharedLogger.error(`Error in onHitEntity hook: ${err}`);
            }
          }
        },
        onMineBlock: async (e) => {
          if (!this.guidebookInstance)
            return;
          for (const hook of this.onMineBlockHooks) {
            try {
              const result = await hook(e, this.guidebookInstance);
              if (result === false) {
                return;
              }
            } catch (err) {
              sharedLogger.error(`Error in onMineBlock hook: ${err}`);
            }
          }
        },
        onUse: async (e) => {
          if (!this.guidebookInstance)
            return;
          for (const hook of this.onUseHooks) {
            try {
              const result = await hook(e, this.guidebookInstance);
              if (result === false) {
                return;
              }
            } catch (err) {
              sharedLogger.error(`Error in onUse hook: ${err}`);
            }
          }
          if (e.source instanceof Player6) {
            const player = e.source;
            const blockHit = player.getBlockFromViewDirection();
            try {
              if (blockHit && blockHit.block.location.x < player.location.x + 3 && blockHit.block.location.x > player.location.x - 3 && blockHit.block.location.y < player.location.y + 3 && blockHit.block.location.y > player.location.y - 3 && blockHit.block.location.z < player.location.z + 3 && blockHit.block.location.z > player.location.z - 3) {
                const block = blockHit.block;
                sharedLogger.debug(`Player targeting block: ${block.typeId}`);
                for (const hook of this.onUseOnHooks) {
                  try {
                    const result = await hook(e, this.guidebookInstance);
                    if (result === false) {
                      return;
                    }
                  } catch (err) {
                    sharedLogger.error(`Error in onUseOn hook: ${err}`);
                  }
                }
                const associatedPageId = this.findPageByAssociatedBlock(block.typeId);
                if (associatedPageId) {
                  sharedLogger.info(`Opening guidebook on page "${associatedPageId}" for block "${block.typeId}"`);
                  this.guidebookInstance.open(player, associatedPageId);
                  return;
                }
              }
            } catch (error) {
              console.warn(`Failed to open guidebook on block: ${error}`);
            }
          }
          if (e.source instanceof Player6) {
            this.guidebookInstance.open(e.source);
          }
        }
      };
      event.itemComponentRegistry.registerCustomComponent(this.componentId, component);
      this.isRegistered = true;
      sharedLogger.info(`Registered item component: ${this.componentId}`);
    };
    if (system14.beforeEvents) {
      system14.beforeEvents.startup.subscribe((event) => {
        onStartup(event);
      });
    } else if (world13 && world13.beforeEvents.worldInitialize) {
      world13.beforeEvents.worldInitialize.subscribe((event) => {
        onStartup(event);
      });
    }
    return this;
  }
  getHookStats() {
    return {
      onBeforeDurabilityDamage: this.onBeforeDurabilityDamageHooks.length,
      onCompleteUse: this.onCompleteUseHooks.length,
      onConsume: this.onConsumeHooks.length,
      onHitEntity: this.onHitEntityHooks.length,
      onMineBlock: this.onMineBlockHooks.length,
      onUse: this.onUseHooks.length,
      onUseOn: this.onUseOnHooks.length
    };
  }
};

// data/gametests/node_modules/@5-frame-studios/guidebook/dist/core/Guidebook.js
var GUIDEBOOK_COMPONENT_ID = "guide:is_guidebook";
var LAST_OPENED_PAGE_PROPERTY = "guidebook_last_page";
var Guidebook = class {
  /**
   * Creates a new Guidebook instance.
   *
   * @param data The guidebook data containing all page definitions
   * @param options Optional configuration options
   * @param options.debugMode Whether to enable debug mode (default: false)
   * @param options.logLevel Global log level for the entire guidebook system (default: "debug")
   *
   * @example
   * ```typescript
   * const guidebook = new Guidebook({
   *   pages: [
   *     { id: "main", title: "Main Menu", body: "Welcome!" }
   *   ]
   * }, { debugMode: true, logLevel: "info" });
   * ```
   */
  constructor(data, options) {
    this.pageDefs = /* @__PURE__ */ new Map();
    this.actions = /* @__PURE__ */ new Map();
    this.textParsers = /* @__PURE__ */ new Map();
    this.playerNavStacks = /* @__PURE__ */ new Map();
    this.openPlayers = /* @__PURE__ */ new Set();
    this.debugMode = options?.debugMode ?? false;
    sharedLogger.setLogLevel(options?.logLevel ?? "debug");
    this._flattenPages(data.pages);
    this.pageManager = new PageManager(this);
    this.debugManager = new DebugManager(this);
    this.formBuilder = new FormBuilder(this);
    this.eventManager = new EventManager(this);
    this.propertyManager = new PropertyManager(this);
    this.itemManager = new ItemManager(this, GUIDEBOOK_COMPONENT_ID);
    if (this.debugMode) {
      this.debugManager.setup();
    }
    sharedLogger.info(`Loaded ${this.pageDefs.size} page definitions.${this.debugMode ? " Debug mode enabled." : ""}`);
  }
  // --- Public API Methods ---
  /**
   * Opens the guidebook for a specific player.
   *
   * This method will show the guidebook UI to the player, either opening
   * to the specified page or the last opened page, or defaulting to "main".
   *
   * @param player The player to open the guidebook for
   * @param pageId Optional page to open to (defaults to last opened page or home)
   *
   * @example
   * ```typescript
   * guidebook.open(player, "tutorial");
   * ```
   */
  open(player, pageId) {
    const targetPage = pageId || this.getLastOpenedPage(player) || "main";
    this.openPlayers.add(player.id);
    this._showPage(player, targetPage);
  }
  /**
   * Closes the guidebook for a specific player.
   *
   * Note: This method tracks the closed state but cannot programmatically
   * close UI forms in Minecraft. It prevents further interactions.
   *
   * @param player The player to close the guidebook for
   *
   * @example
   * ```typescript
   * guidebook.close(player);
   * ```
   */
  close(player) {
    this.openPlayers.delete(player.id);
    this.playerNavStacks.delete(player.id);
  }
  /**
   * Checks if the guidebook is currently open for a player.
   *
   * @param player The player to check
   * @returns True if the guidebook is open for this player
   *
   * @example
   * ```typescript
   * if (guidebook.isOpen(player)) {
   *   console.log(`${player.name} has the guidebook open`);
   * }
   * ```
   */
  isOpen(player) {
    return this.openPlayers.has(player.id);
  }
  /**
   * Gets a page definition by ID.
   *
   * @param pageId The ID of the page to retrieve
   * @returns The page definition or undefined if not found
   *
   * @example
   * ```typescript
   * const page = guidebook.getPage("tutorial");
   * if (page) {
   *   console.log(`Found page: ${page.title}`);
   * }
   * ```
   */
  getPage(pageId) {
    return this.pageDefs.get(pageId);
  }
  /**
   * Adds a new page to the guidebook.
   *
   * @param page The page definition to add
   * @returns This guidebook instance for chaining
   * @throws Error if the page doesn't have an ID
   *
   * @example
   * ```typescript
   * guidebook.addPage({
   *   id: "new_page",
   *   title: "New Page",
   *   body: "This is a new page"
   * });
   * ```
   */
  addPage(page) {
    if (!page.id) {
      throw new Error("Page must have an ID");
    }
    this.pageDefs.set(page.id, page);
    if (page.children) {
      this._flattenPages(page.children);
    }
    sharedLogger.info(`Added page: ${page.id}`);
    return this;
  }
  /**
   * Updates an existing page in the guidebook.
   *
   * @param pageId The ID of the page to update
   * @param page The new page definition
   * @returns This guidebook instance for chaining
   * @throws Error if the page doesn't exist
   *
   * @example
   * ```typescript
   * guidebook.updatePage("tutorial", {
   *   id: "tutorial",
   *   title: "Updated Tutorial",
   *   body: "Updated content"
   * });
   * ```
   */
  updatePage(pageId, page) {
    if (!this.pageDefs.has(pageId)) {
      throw new Error(`Page ${pageId} does not exist`);
    }
    this.pageDefs.set(pageId, page);
    if (page.children) {
      this._flattenPages(page.children);
    }
    sharedLogger.info(`Updated page: ${pageId}`);
    return this;
  }
  /**
   * Removes a page from the guidebook.
   *
   * @param pageId The ID of the page to remove
   * @returns This guidebook instance for chaining
   *
   * @example
   * ```typescript
   * guidebook.removePage("old_page");
   * ```
   */
  removePage(pageId) {
    if (!this.pageDefs.has(pageId)) {
      sharedLogger.warn(`Attempted to remove non-existent page: ${pageId}`);
      return this;
    }
    this.pageDefs.delete(pageId);
    sharedLogger.info(`Removed page: ${pageId}`);
    return this;
  }
  /**
   * Gets the current navigation state for a player.
   *
   * @param player The player to get state for
   * @returns Object containing navigation stack and current page
   *
   * @example
   * ```typescript
   * const state = guidebook.getPlayerState(player);
   * console.log(`Current page: ${state.currentPage}`);
   * console.log(`Navigation stack: ${state.navStack.join(' -> ')}`);
   * ```
   */
  getPlayerState(player) {
    const navStack = this.playerNavStacks.get(player.id) || [];
    return {
      navStack: [...navStack],
      currentPage: navStack[navStack.length - 1]
    };
  }
  /**
   * Resets a player's guidebook state.
   *
   * This clears their navigation stack, marks them as not having the guidebook open,
   * and clears their last opened page property.
   *
   * @param player The player to reset state for
   * @returns This guidebook instance for chaining
   *
   * @example
   * ```typescript
   * guidebook.resetPlayerState(player);
   * ```
   */
  resetPlayerState(player) {
    this.playerNavStacks.delete(player.id);
    this.openPlayers.delete(player.id);
    player.setDynamicProperty(LAST_OPENED_PAGE_PROPERTY, void 0);
    sharedLogger.info(`Reset state for player: ${player.name}`);
    return this;
  }
  /**
   * Gets the component ID used for item registration.
   *
   * @returns The component ID string
   *
   * @example
   * ```typescript
   * const componentId = guidebook.getComponentId();
   * // Returns "guide:is_guidebook"
   * ```
   */
  getComponentId() {
    return GUIDEBOOK_COMPONENT_ID;
  }
  /**
   * Gets all registered page IDs.
   *
   * @returns Array of all page IDs
   *
   * @example
   * ```typescript
   * const pageIds = guidebook.getPageIds();
   * console.log(`Available pages: ${pageIds.join(', ')}`);
   * ```
   */
  getPageIds() {
    return Array.from(this.pageDefs.keys());
  }
  /**
   * Gets all registered action names.
   *
   * @returns Array of all action names
   *
   * @example
   * ```typescript
   * const actionNames = guidebook.getActionNames();
   * console.log(`Available actions: ${actionNames.join(', ')}`);
   * ```
   */
  getActionNames() {
    return Array.from(this.actions.keys());
  }
  /**
   * Gets all registered text parser names.
   *
   * @returns Array of all text parser names
   *
   * @example
   * ```typescript
   * const parserNames = guidebook.getTextParserNames();
   * console.log(`Available parsers: ${parserNames.join(', ')}`);
   * ```
   */
  getTextParserNames() {
    return Array.from(this.textParsers.keys());
  }
  /**
   * Checks if debug mode is enabled.
   *
   * @returns True if debug mode is enabled
   *
   * @example
   * ```typescript
   * if (guidebook.isDebugMode()) {
   *   console.log("Debug mode is active");
   * }
   * ```
   */
  isDebugMode() {
    return this.debugMode;
  }
  /**
   * Navigates a player to a specific page.
   *
   * @param player The player to navigate
   * @param pageId The page to navigate to
   *
   * @example
   * ```typescript
   * guidebook.navigateTo(player, "next_page");
   * ```
   */
  navigateTo(player, pageId) {
    this._showPage(player, pageId);
  }
  /**
   * Triggers an action programmatically for a player.
   *
   * This method allows external code to trigger any action that can be executed
   * from guidebook pages, including navigation actions, custom registered actions,
   * and built-in actions like search.
   *
   * @param player The player to trigger the action for
   * @param action The action to trigger (string, object, or array of actions)
   * @param formValues Optional form values to pass to the action
   *
   * @example
   * ```typescript
   * // Trigger a navigation action
   * guidebook.triggerAction(player, "navigateTo:tutorial");
   *
   * // Trigger a custom registered action
   * guidebook.triggerAction(player, "give_reward");
   *
   * // Trigger a search action with form values
   * guidebook.triggerAction(player, "search", ["weapon"]);
   *
   * // Trigger multiple actions
   * guidebook.triggerAction(player, ["navigateTo:main", "give_reward"]);
   *
   * // Trigger a property-setting action
   * guidebook.triggerAction(player, {
   *   action: "set_properties",
   *   properties: [
   *     { property: "tutorial_completed", value: true }
   *   ]
   * });
   * ```
   */
  triggerAction(player, action, formValues) {
    sharedLogger.debug(`Triggering action for player ${player.name}: ${JSON.stringify(action)}`);
    if (!action) {
      sharedLogger.warn(`Attempted to trigger null/undefined action for player ${player.name}`);
      return;
    }
    if (Array.isArray(action)) {
      sharedLogger.debug(`Executing array of ${action.length} actions for player ${player.name}`);
      action.forEach((singleAction, index) => {
        sharedLogger.debug(`  Executing action ${index + 1}/${action.length}: ${JSON.stringify(singleAction)}`);
        this.triggerAction(player, singleAction, formValues);
      });
      return;
    }
    if (typeof action === "object") {
      if (action.action === "set_properties") {
        sharedLogger.debug(`Setting properties for player ${player.name}: ${JSON.stringify(action.properties)}`);
        action.properties.forEach((propInfo) => {
          this.propertyManager.setProperty(player, propInfo.property, propInfo.value);
        });
      } else {
        sharedLogger.warn(`Unknown object action type: ${action.action}`);
      }
      return;
    }
    const navStack = this.getPlayerNavStacks().get(player.id) || [];
    if (action.startsWith("navigateTo:")) {
      const pageId = action.substring(11);
      sharedLogger.debug(`Navigating player ${player.name} to page: ${pageId}`);
      this.navigateTo(player, pageId);
    } else if (action === "back") {
      sharedLogger.debug(`Navigating player ${player.name} back`);
      navStack.pop();
      const previousPage = navStack.pop();
      this.navigateTo(player, previousPage || "main");
    } else if (action === "close") {
      sharedLogger.debug(`Closing guidebook for player ${player.name}`);
      this.setLastOpenedPage(player, navStack[navStack.length - 1]);
      this.getPlayerNavStacks().delete(player.id);
      this.getOpenPlayers().delete(player.id);
    } else if (action === "search" && formValues && formValues.length > 0) {
      sharedLogger.debug(`Triggering search action for player ${player.name} with term: ${formValues[0]}`);
      this.pageManager.performSearch(player, formValues[0]);
    } else if (action === "search") {
      sharedLogger.warn(`Search action triggered for player ${player.name} but no form values provided`);
    } else if (this.getActions().has(action)) {
      sharedLogger.debug(`Executing registered action "${action}" for player ${player.name}`);
      this.getActions().get(action)(player, formValues);
    } else {
      sharedLogger.warn(`Unhandled action "${action}" for player ${player.name}`);
    }
  }
  // --- Internal Methods ---
  /**
   * Flattens nested page structures into a flat map.
   *
   * This method recursively processes all pages and their children,
   * storing them in the pageDefs map for easy access.
   *
   * @param pages Array of pages to flatten
   *
   * @private
   */
  _flattenPages(pages) {
    for (const page of pages) {
      if (!page.id) {
        sharedLogger.warn("Found a page without an ID, it will be ignored." + JSON.stringify(page));
        continue;
      }
      if (this.pageDefs.has(page.id)) {
        const existingPage = this.pageDefs.get(page.id);
        sharedLogger.error(`\u26A0\uFE0F  DUPLICATE PAGE ID DETECTED! \u26A0\uFE0F`);
        sharedLogger.error(`Page ID "${page.id}" is used by multiple pages:`);
        sharedLogger.error(`  Existing page: title="${existingPage.title}", fields=${existingPage.fields?.length || 0}, buttons=${existingPage.buttons?.length || 0}`);
        sharedLogger.error(`  New page: title="${page.title}", fields=${page.fields?.length || 0}, buttons=${page.buttons?.length || 0}`);
        sharedLogger.error(`The new page will overwrite the existing one, which may cause unexpected behavior!`);
        sharedLogger.error(`Please ensure all page IDs are unique.`);
      }
      this.pageDefs.set(page.id, page);
      sharedLogger.debug(`Added page: ID="${page.id}", title="${page.title}", fields=${page.fields?.length || 0}, buttons=${page.buttons?.length || 0}`);
      if (page.children) {
        this._flattenPages(page.children);
      }
    }
  }
  /**
   * Registers a custom action callback.
   *
   * @param name The name of the action (used in JSON configurations)
   * @param callback The function to execute when the action is triggered
   * @returns This guidebook instance for chaining
   *
   * @example
   * ```typescript
   * guidebook.registerAction("teleport_home", (player) => {
   *   player.teleport({ x: 0, y: 64, z: 0 });
   * });
   * ```
   */
  registerAction(name, callback) {
    this.actions.set(name, callback);
    return this;
  }
  /**
   * Registers a custom text parser callback.
   *
   * @param name The name of the parser (used in {{parser:name}} syntax)
   * @param callback The function that returns the parsed text
   * @returns This guidebook instance for chaining
   *
   * @example
   * ```typescript
   * guidebook.registerTextParser("player_name", (player) => {
   *   return player.name;
   * });
   * ```
   */
  registerTextParser(name, callback) {
    this.textParsers.set(name, callback);
    return this;
  }
  /**
   * Gets a setting value for a player.
   *
   * @param player The player to get the setting for
   * @param name The name of the setting
   * @returns The setting value
   *
   * @example
   * ```typescript
   * const setting = guidebook.getSetting(player, "sound_enabled");
   * ```
   */
  getSetting(player, name) {
    return player.getDynamicProperty(name);
  }
  /**
   * Gets the last opened page for a player.
   *
   * @param player The player to get the last page for
   * @returns The page ID or undefined if no page was opened
   *
   * @example
   * ```typescript
   * const lastPage = guidebook.getLastOpenedPage(player);
   * if (lastPage) {
   *   guidebook.open(player, lastPage);
   * }
   * ```
   */
  getLastOpenedPage(player) {
    return player.getDynamicProperty(LAST_OPENED_PAGE_PROPERTY);
  }
  /**
   * Sets the last opened page for a player.
   *
   * @param player The player to set the last page for
   * @param pageId The page ID to remember
   *
   * @example
   * ```typescript
   * guidebook.setLastOpenedPage(player, "tutorial");
   * ```
   */
  setLastOpenedPage(player, pageId) {
    player.setDynamicProperty(LAST_OPENED_PAGE_PROPERTY, pageId);
  }
  /**
   * Shows a popup message to a player.
   *
   * @param player The player to show the popup to
   * @param title The popup title
   * @param body The popup body text
   *
   * @example
   * ```typescript
   * Guidebook.showPopup(player, "Welcome!", "Thanks for using the guidebook!");
   * ```
   */
  static showPopup(player, title, body) {
    new MessageFormData3().title(title).body(body).button1("OK").button2("OK").show(player);
  }
  /**
   * Shows a dynamic page to a player.
   *
   * @param player The player to show the page to
   * @param page The dynamic page to show
   *
   * @example
   * ```typescript
   * const dynamicPage = Guidebook.createActionPage()
   *   .title("Dynamic Page")
   *   .body("This page was created programmatically")
   *   .addButton("OK", "close")
   *   .build();
   *
   * Guidebook.showPage(player, dynamicPage);
   * ```
   */
  static showPage(player, page) {
    if (!page.title) {
      sharedLogger.warn(`Attempted to call showPage with a page without a title. Is it a page with versions?`);
      return;
    }
    const title = page.title && page.title.trim() ? page.title : "Guidebook";
    const body = page.body && page.body.trim() ? page.body : "";
    const form = new ActionFormData2().title(title);
    if (body) {
      form.body(body);
    }
    page.buttons?.forEach((btn, index) => {
      const buttonText = btn.text && btn.text.trim() ? btn.text : `Button ${index + 1}`;
      form.button(buttonText, btn.icon);
    });
    form.show(player);
  }
  /**
   * Creates a new action page builder for dynamic page creation.
   *
   * @returns A new ActionPageBuilder instance
   *
   * @example
   * ```typescript
   * const page = Guidebook.createActionPage()
   *   .title("Welcome")
   *   .body("Hello, world!")
   *   .addButton("Continue", "navigateTo:next")
   *   .build();
   * ```
   */
  static createActionPage() {
    return new ActionPageBuilder();
  }
  /**
   * Initializes the guidebook system.
   *
   * This method sets up the item component registration that allows
   * items with the guidebook component to open the guidebook when used.
   *
   * @example
   * ```typescript
   * guidebook.init();
   * ```
   */
  init() {
    this.itemManager.registerComponent();
    sharedLogger.info("Guidebook system initialized and waiting for startup.");
  }
  /**
   * Opens the guidebook when an item is used.
   *
   * @param player The player who used the item
   *
   * @private
   */
  _openBook(player) {
    system15.run(() => {
      const lastPage = this.getLastOpenedPage(player);
      this.open(player, lastPage || "main");
    });
  }
  /**
   * Shows a page to a player.
   *
   * This method handles page version resolution, navigation stack management,
   * event triggering, and form building.
   *
   * @param player The player to show the page to
   * @param pageId The ID of the page to show
   *
   * @private
   */
  _showPage(player, pageId) {
    let pageDef = this.pageDefs.get(pageId);
    sharedLogger.debug(`Showing page ${pageId} to ${player.name}`);
    if (!pageDef) {
      sharedLogger.error(`\u274C Page "${pageId}" not found! Available pages: ${Array.from(this.pageDefs.keys()).join(", ")}`);
      if (pageId !== "main") {
        sharedLogger.warn(`\u{1F504} Falling back to "main" page for ${player.name}`);
        this._showPage(player, "main");
        return;
      } else {
        sharedLogger.error(`\u{1F4A5} CRITICAL: "main" page not found! Cannot show any page to ${player.name}`);
        this.getOpenPlayers().delete(player.id);
        return;
      }
    }
    sharedLogger.debug(`\u{1F4C4} Found page: ID="${pageDef.id}", title="${pageDef.title}", fields=${pageDef.fields?.length || 0}, buttons=${pageDef.buttons?.length || 0}`);
    const resolvedPageDef = this._resolvePageVersion(player, pageDef);
    sharedLogger.debug(`\u{1F4C4} Resolved page: ID="${resolvedPageDef.id}", title="${resolvedPageDef.title}", fields=${resolvedPageDef.fields?.length || 0}, buttons=${resolvedPageDef.buttons?.length || 0}`);
    const navStack = this.playerNavStacks.get(player.id) || [];
    if (navStack[navStack.length - 1] !== pageId) {
      navStack.push(pageId);
      this.playerNavStacks.set(player.id, navStack);
    }
    this.eventManager.handlePageEvents("on_first_open", resolvedPageDef, player);
    this.eventManager.handlePageEvents("on_open", resolvedPageDef, player);
    const title = this.propertyManager.parseText(player, resolvedPageDef.title || "UNABLE TO FIND TITLE");
    const body = this.propertyManager.parseText(player, resolvedPageDef.body ?? "");
    sharedLogger.debug(`\u{1F4C4} Parsed content: title="${title}", body="${body.substring(0, 100)}${body.length > 100 ? "..." : ""}"`);
    sharedLogger.debug(`\u{1F4C4} Page "${resolvedPageDef.id}" has ${resolvedPageDef.fields?.length || 0} fields`);
    sharedLogger.debug(`\u{1F4C4} Form type selection: ${resolvedPageDef.fields && resolvedPageDef.fields.length > 0 ? "ModalForm" : "ActionForm"}`);
    if (resolvedPageDef.fields && resolvedPageDef.fields.length > 0) {
      sharedLogger.debug(`\u{1F527} Building ModalForm for page "${resolvedPageDef.id}"`);
      this.formBuilder.buildModalForm(player, resolvedPageDef, title, body);
    } else {
      sharedLogger.debug(`\u{1F527} Building ActionForm for page "${resolvedPageDef.id}"`);
      this.formBuilder.buildActionForm(player, resolvedPageDef, title, body);
    }
  }
  /**
   * Resolves the appropriate version of a page based on player properties.
   *
   * @param player The player to resolve the version for
   * @param pageDef The page definition to resolve
   * @returns The resolved page definition
   * @throws Error if version resolution fails
   *
   * @private
   */
  _resolvePageVersion(player, pageDef) {
    if (!pageDef) {
      sharedLogger.warn(`_resolvePageVersion called without a pagedef. Defaulting to main`);
      pageDef = this.pageDefs.get("main");
      if (!pageDef) {
        throw new Error(`Defaulted to main but was unable to find the main page.`);
      }
    }
    if (!pageDef.versions) {
      return pageDef;
    }
    const versionControlProperty = pageDef.version_control_property;
    if (!versionControlProperty) {
      throw new Error(`Page ${pageDef.id} has versions defined without a version control property.`);
    }
    const vcpValue = this.propertyManager.getProperty(player, versionControlProperty);
    let page;
    page = pageDef.versions.find((v) => {
      if (v.value == vcpValue)
        return v;
    });
    if (!page) {
      sharedLogger.warn(`Unable to resolve version ${vcpValue} for versions on ${pageDef.id}. Defaulting to 'default'`);
      page = pageDef.versions.find((v) => {
        if (v.value == 0)
          return v;
      });
    }
    if (!page) {
      throw new Error(`Unable to resolve version ${vcpValue} for versions on ${pageDef.id} and no default (value 'default') was found.`);
    }
    return {
      id: `${pageDef.id}.${page.value}`,
      ...page
    };
  }
  // --- Getters for managers ---
  /**
   * Gets the page definitions map.
   *
   * @returns Map of all page definitions
   *
   * @example
   * ```typescript
   * const pageDefs = guidebook.getPageDefs();
   * console.log(`Total pages: ${pageDefs.size}`);
   * ```
   */
  getPageDefs() {
    return this.pageDefs;
  }
  /**
   * Gets the registered actions map.
   *
   * @returns Map of all registered action callbacks
   *
   * @example
   * ```typescript
   * const actions = guidebook.getActions();
   * console.log(`Total actions: ${actions.size}`);
   * ```
   */
  getActions() {
    return this.actions;
  }
  /**
   * Gets the registered text parsers map.
   *
   * @returns Map of all registered text parser callbacks
   *
   * @example
   * ```typescript
   * const parsers = guidebook.getTextParsers();
   * console.log(`Total parsers: ${parsers.size}`);
   * ```
   */
  getTextParsers() {
    return this.textParsers;
  }
  /**
   * Gets the player navigation stacks map.
   *
   * @returns Map of all player navigation stacks
   *
   * @example
   * ```typescript
   * const navStacks = guidebook.getPlayerNavStacks();
   * console.log(`Players with navigation history: ${navStacks.size}`);
   * ```
   */
  getPlayerNavStacks() {
    return this.playerNavStacks;
  }
  /**
   * Gets the set of players with open guidebooks.
   *
   * @returns Set of player IDs with open guidebooks
   *
   * @example
   * ```typescript
   * const openPlayers = guidebook.getOpenPlayers();
   * console.log(`Players with open guidebooks: ${openPlayers.size}`);
   * ```
   */
  getOpenPlayers() {
    return this.openPlayers;
  }
};
var ActionPageBuilder = class {
  constructor() {
    this.page = {
      id: Symbol("dynamicPage"),
      title: "",
      buttons: []
    };
  }
  /**
   * Sets the title of the page.
   *
   * @param text The title text
   * @returns This builder instance for chaining
   *
   * @example
   * ```typescript
   * builder.title("Welcome Page");
   * ```
   */
  title(text) {
    this.page.title = text;
    return this;
  }
  /**
   * Sets the body content of the page.
   *
   * @param text The body text
   * @returns This builder instance for chaining
   *
   * @example
   * ```typescript
   * builder.body("This is the main content of the page.");
   * ```
   */
  body(text) {
    this.page.body = text;
    return this;
  }
  /**
   * Adds a button to the page.
   *
   * @param text The button text
   * @param action The action to trigger when the button is clicked
   * @returns This builder instance for chaining
   *
   * @example
   * ```typescript
   * builder.addButton("Continue", "navigateTo:next");
   * ```
   */
  addButton(text, action) {
    this.page.buttons?.push({ text, icon: "", action });
    return this;
  }
  /**
   * Builds the dynamic page.
   *
   * @returns The built dynamic page
   *
   * @example
   * ```typescript
   * const page = new ActionPageBuilder()
   *   .title("Welcome")
   *   .body("Hello, world!")
   *   .addButton("Continue", "navigateTo:next")
   *   .build();
   * ```
   */
  build() {
    return this.page;
  }
};

// json5:C:\Users\Admin\Downloads\commissions\projects\craftable-houses\.regolith\tmp\data\gametests\src\guidebook_data.json
var guidebook_data_default = { pages: [{ title: "\xA7aAccepting & Rejecting Builds", showInSearch: true, buttons: [{ text: "Back to Placement System", action: "navigateTo:placement-system", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "When a build preview is active, your hotbar displays a build menu with accept and reject options.\n\n\xA76Accept Build\xA7r\n\nLocated in hotbar slot 9. Press :_input_key.use: to confirm placement. The structure becomes permanent and your normal hotbar is restored.\n\n\xA76Reject Build\xA7r\n\nLocated in hotbar slot 1. Press :_input_key.use: to cancel placement. The preview disappears and your normal hotbar is restored. No resources are consumed when rejecting a build.", id: "accepting-rejecting" }, { title: "\xA7bHelp & Support", showInSearch: true, buttons: [{ text: "Back to Main Menu", action: "navigateTo:main" }], body: "Need help with the \xA7dCraftable Bases Add-On\xA7r?\n\n\xA76Discord Community\xA7r\nJoin our Discord server: \xA7b5framestudios.com/discord\xA7r\n\n\xA76Support Website\xA7r\nVisit: \xA7bhttps://www.5framestudios.com/support\xA7r\n\n\xA76Email Support\xA7r\nContact: \xA7boffice@5framestudios.com\xA7r", id: "help-support" }, { title: "\xA7dCraftable Bases \xA76Guidebook", showInSearch: true, buttons: [{ text: "Quick Start Guide", action: "navigateTo:quick-start", icon: "textures/5fs/cb/items/house_0_craft" }, { text: "Basic Builds", action: "navigateTo:basic-builds", icon: "textures/5fs/cb/items/creeperhead_craft" }, { text: "Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/5fs/cb/items/netherportal_craft" }, { text: "Placement System", action: "navigateTo:placement-system", icon: "textures/5fs/cb/items/build_settings/accept" }, { text: "Furniture", action: "navigateTo:furniture", icon: "textures/5fs/cb/items/ocean_spawn_eggs/table_turtle" }, { text: "Items & Tools", action: "navigateTo:items", icon: "textures/5fs/cb/items/special_tools/wrench" }, { text: "Help & Support", action: "navigateTo:help-support", icon: "textures/5fs/cb/items/guidebook" }], body: "", id: "main" }, { title: "\xA72Quick Start Guide", showInSearch: true, on_first_open: [{ action: "set_property", property: { name: "tutorial_started", scope: "player" }, value: "true" }], buttons: [{ text: "Basic Builds", action: "navigateTo:basic-builds", icon: "textures/5fs/cb/items/house_0_craft" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Welcome to \xA7dCraftable Bases Add-On\xA7r! This Add-On allows you to find, craft, and place massive structures instantly in your world.\n\n\xA76Getting Started in 3 Easy Steps\xA7r\n\n\xA761.\xA7r \xA7fStart by crafting a basic structure, like a Castle Wall or Urban House, at a :crafting_table: crafting table.\xA7r\n\n\xA762.\xA7r \xA7fPress :_input_key.use: with the Build Item in your hand. A preview will appear, and your hotbar will change to a special build menu.\xA7r\n\n\xA763.\xA7r \xA7fUse the build menu to move and rotate the structure. When you're ready, select the \xA7aAccept Build\xA7r item and press :_input_key.use: to place the structure in the selected location.\xA7r\n\n\xA7e[!] \xA7r \xA7fDon't worry about mistakes! Check the \xA7gPlacement System\xA7r section to learn how to undo builds. The preview's entrance will always face towards you when you first place it. You have \xA7c5 minutes\xA7r to undo a placed structure if needed.\xA7r", id: "quick-start" }, { title: "\xA76Bank", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A large bank structure with multiple floors for storage and organization.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/bank" }, { title: "\xA77Castle Cornerstone", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A cornerpiece structure used to connect castle walls at corners.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/castle-cornerstone" }, { title: "\xA77Castle Wall", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A castle wall structure used to enclose areas for protection.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/castle-wall" }, { title: "\xA72Creeper Head", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A house built inside a creeper head structure with multiple rooms for survival.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/creeper-head" }, { title: "\xA73Lakeside Pagoda", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A pagoda structure with traditional Asian architecture and multi-level design.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/lakeside-pagoda" }, { title: "\xA76Large Mansion", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A large mansion structure with multiple rooms, stories, and pools.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/large-mansion" }, { title: "\xA7eLucky Block", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A house structure built inside a lucky block with gaming-themed design.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/lucky-block" }, { title: "\xA72Basic Builds", showInSearch: true, buttons: [{ text: "Creeper Head", action: "navigateTo:basic-builds/creeper-head", icon: "textures/5fs/cb/items/creeperhead_craft" }, { text: "Sports Cafe", action: "navigateTo:basic-builds/sports-cafe", icon: "textures/5fs/cb/items/sportsbar_craft" }, { text: "Bank", action: "navigateTo:basic-builds/bank", icon: "textures/5fs/cb/items/bank_craft" }, { text: "Castle Wall", action: "navigateTo:basic-builds/castle-wall", icon: "textures/5fs/cb/items/bridge_0_craft" }, { text: "Castle Cornerstone", action: "navigateTo:basic-builds/castle-cornerstone", icon: "textures/5fs/cb/items/bridge_1_craft" }, { text: "Skull", action: "navigateTo:basic-builds/skull", icon: "textures/5fs/cb/items/skull_craft" }, { text: "Lakeside Pagoda", action: "navigateTo:basic-builds/lakeside-pagoda", icon: "textures/5fs/cb/items/smalltower_craft" }, { text: "Mini Mansion", action: "navigateTo:basic-builds/mini-mansion", icon: "textures/5fs/cb/items/modernhouse_0_craft" }, { text: "Large Mansion", action: "navigateTo:basic-builds/large-mansion", icon: "textures/5fs/cb/items/modernhouse_1_craft" }, { text: "Urban Farmhouse", action: "navigateTo:basic-builds/urban-farmhouse", icon: "textures/5fs/cb/items/house_0_craft" }, { text: "Suburban House", action: "navigateTo:basic-builds/suburban-house", icon: "textures/5fs/cb/items/house_1_craft" }, { text: "Urban House", action: "navigateTo:basic-builds/urban-house", icon: "textures/5fs/cb/items/house_2_craft" }, { text: "Lucky Block", action: "navigateTo:basic-builds/lucky-block", icon: "textures/5fs/cb/items/luckyblock_craft" }, { text: "Modern Hotel", action: "navigateTo:basic-builds/modern-hotel", icon: "textures/5fs/cb/items/modernhotel_craft" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Structures that can be crafted immediately without special requirements.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for each structure's recipe. All basic builds can be placed, moved, and rotated before confirming placement.", id: "basic-builds" }, { title: "\xA76Mini Mansion", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A mansion structure with multiple rooms and pools in a compact design.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/mini-mansion" }, { title: "\xA79Modern Hotel", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A hotel structure with multiple rooms across multiple stories.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/modern-hotel" }, { title: "\xA78Skull", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A house built inside a skeletal skull structure with multiple interior rooms.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/skull" }, { title: "\xA7eSports Cafe", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A cafe structure with sports-themed design and dining areas.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/sports-cafe" }, { title: "\xA72Suburban House", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A house structure with multiple rooms designed for suburban living.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/suburban-house" }, { title: "\xA7aUrban Farmhouse", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A house structure designed for farmland areas with room for 1-2 people.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/urban-farmhouse" }, { title: "\xA79Urban House", showInSearch: true, buttons: [{ text: "Back to Basic Builds", action: "navigateTo:basic-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A house structure designed for individual living with room for expansion.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aUnlock Method:\xA7r \xA7fAvailable from start\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.", id: "basic-builds/urban-house" }, { title: "\xA76Furniture", showInSearch: true, buttons: [{ text: "Back to Main Menu", action: "navigateTo:main" }], body: "There are various furniture items that fit almost every build and biome.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bRequirements:\xA7r \xA7fNone\xA7r\n\xA7aTools Available:\xA7r \xA7fRuler, Sledgehammer, Wrench\xA7r\n\n\xA76Tool Functions\xA7r\n\n\xA7bWrench:\xA7r Rotate furniture to change orientation\n\n\xA7cSledgehammer:\xA7r Remove furniture and collect it back to your inventory\n\n\xA75Ruler:\xA7r Adjust positioning of doors and tables to center them on blocks\n\nCheck the :crafting_table: crafting table for all furniture recipes.", id: "furniture" }, { title: "\xA76Tools & Items", showInSearch: true, buttons: [{ text: "Ruler", action: "navigateTo:items/ruler", icon: "textures/5fs/cb/items/special_tools/ruler" }, { text: "Sledgehammer", action: "navigateTo:items/sledgehammer", icon: "textures/5fs/cb/items/special_tools/sledgehammer" }, { text: "Wrench", action: "navigateTo:items/wrench", icon: "textures/5fs/cb/items/special_tools/wrench" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "", id: "items" }, { title: "\xA75Ruler", showInSearch: true, buttons: [{ text: "Back to Items & Tools", action: "navigateTo:items", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Adjusts the positioning of doors and tables to center them on blocks.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bReloadable:\xA7r \xA7fNo\xA7r  \n\xA7aToggleable:\xA7r \xA7fNo\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.\n\nHold the Ruler and press :_input_key.use: while looking at doors or tables to adjust their positioning and center them properly on blocks. The item does not break during use.", id: "items/paint-brush" }, { title: "\xA75Ruler", showInSearch: true, buttons: [{ text: "Back to Items & Tools", action: "navigateTo:items", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Adjusts the positioning of doors and tables to center them on blocks.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bReloadable:\xA7r \xA7fNo\xA7r  \n\xA7aToggleable:\xA7r \xA7fNo\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.\n\nHold the Ruler and press :_input_key.use: while looking at doors or tables to adjust their positioning and center them properly on blocks. The item does not break during use.", id: "items/ruler" }, { title: "\xA7cSledgehammer", showInSearch: true, buttons: [{ text: "Back to Items & Tools", action: "navigateTo:items", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Destroys and collects furniture items.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bReloadable:\xA7r \xA7fNo\xA7r\n\xA7aToggleable:\xA7r \xA7fNo\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.\n\nHold the Sledgehammer and press :_input_key.attack: while looking at furniture to break and collect it. The furniture item is added to your inventory.", id: "items/sledgehammer" }, { title: "\xA7bWrench", showInSearch: true, buttons: [{ text: "Back to Items & Tools", action: "navigateTo:items", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Rotates furniture items to change their orientation.\n\n\xA76Craftable:\xA7r \xA7fYes\xA7r\n\xA7bReloadable:\xA7r \xA7fNo\xA7r\n\xA7aToggleable:\xA7r \xA7fNo\xA7r\n\nCheck the :crafting_table: crafting table for the recipe.\n\nHold the Wrench and press :_input_key.use: while looking at furniture to rotate it in 90-degree increments. The item does not break or consume the furniture during use.", id: "items/wrench" }, { title: "\xA7aAccepting & Rejecting Builds", showInSearch: true, buttons: [{ text: "Back to Placement System", action: "navigateTo:placement-system", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Once a build preview is active, your hotbar transforms into a build menu. The two main options are positioned on the far left and right slots.\n\n\xA76Accept Build\xA7r\n\nThe \xA7aAccept Build\xA7r item appears in your last hotbar slot \xA77(slot 9)\xA7r. \xA7fPress :_input_key.use: while holding it to confirm the placement at the current preview position. This action places the structure permanently in your world and returns your normal hotbar.\xA7r\n\n\xA76Reject Build\xA7r\n\nThe \xA7cReject Build\xA7r item appears in your first hotbar slot \xA77(slot 1)\xA7r. \xA7fPress :_input_key.use: on this item to cancel the placement entirely. The preview disappears, no structure is placed, and your normal hotbar is immediately restored.\xA7r\n\n\xA76Process Flow\xA7r\n\nWhen you press :_input_key.use: with a build item, the placement sequence begins. A particle outline shows the structure location while your hotbar changes to the build menu. Position and adjust the structure using the movement controls, then make your final decision using either the Accept or Reject options.\n\n\xA7e[!] \xA7rAlways check the preview carefully before accepting. Your normal hotbar is safely stored during placement, and no resources are lost when rejecting a build.", id: "placement-system/accepting-rejecting" }, { title: "\xA7aConfirming & Undoing Builds", showInSearch: true, buttons: [{ text: "Back to Placement System", action: "navigateTo:placement-system", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Once you're satisfied with the placement position, you can confirm it to create the structure permanently. If you change your mind after placing, you have a limited time window to undo the placement.\n\n\xA76Confirming Placement\xA7r\n\nPress :_input_key.use: on the \xA7aAccept Build\xA7r item in slot 9 to place the structure permanently. The particle preview becomes a real structure in your world, your normal hotbar is restored, and the build item is consumed from your inventory.\n\n\xA76Undo System\xA7r\n\nAfter placing a structure, a special \xA7cundo item\xA7r appears in your hotbar with a \xA7c5-minute\xA7r countdown timer. Press :_input_key.use: on this item to completely remove the structure from the world and recover your original build item.\n\n\xA7e[!] \xA7rYou must act within the 5-minute window to undo a placement. Each undo item can only be used once, and you cannot undo just part of a structure. Always double-check your placement before accepting, and keep the undo item handy if you're unsure about the position.", id: "placement-system/confirming-undoing" }, { title: "\xA7aPlacement System", showInSearch: true, buttons: [{ text: "Accepting & Rejecting Builds", action: "navigateTo:placement-system/accepting-rejecting", icon: "textures/5fs/cb/items/build_settings/accept" }, { text: "Moving & Previewing a Build", action: "navigateTo:placement-system/moving-previewing", icon: "textures/5fs/cb/items/build_settings/move_north" }, { text: "Confirming & Undoing a Build", action: "navigateTo:placement-system/confirming-undoing", icon: "textures/5fs/cb/items/build_settings/restore_terrain" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "The placement system allows positioning structures before confirming their placement. You can move, rotate, and preview builds before making them permanent.\n\nPress :_input_key.use: with a build item to display a particle outline showing where the structure will be placed. Your hotbar transforms into a build menu with positioning tools.\n\nThe system allows movement one block at a time and rotation in 90-degree increments. An undo system removes structures within \xA7c5 minutes\xA7r of placement. The preview's entrance faces towards you initially.", id: "placement-system" }, { title: "\xA7aMoving & Previewing Builds", showInSearch: true, buttons: [{ text: "Back to Placement System", action: "navigateTo:placement-system", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Once you activate a build item, you'll see a particle preview and gain access to movement controls to position your structure before placement.\n\n\xA76Preview System\xA7r\n\nA particle outline shows where your structure will be placed, updating as you adjust the positioning. The preview's entrance faces towards you initially, and the system includes collision detection to show whether placement is valid or blocked.\n\n\xA76Movement Controls\xA7r\n\nYour build menu hotbar contains items for moving the structure forward, backward, left, right, up, and down. Additional controls rotate the structure in 90-degree increments.\n\nThe hotbar contains directional movement, rotation controls, and the Accept or Reject options for completing the placement process.", id: "placement-system/moving-previewing" }, { title: "\xA7aAnimal Barn", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A barn with multiple stalls for housing farm animals.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fSavannah Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Savannah Biome\xA7r\n\nDiscover the Savannah Biome to unlock this structure.", id: "unlockable-builds/animal-barn" }, { title: "\xA72Bedbug", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A home built within a giant bedbug structure for swamp environments.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fMangrove Swamp or Swamp Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Mangrove Swamp or Swamp Biome\xA7r\n\nTo unlock this structure, discover the Mangrove Swamp or Swamp Biome by exploring your world.", id: "unlockable-builds/bedbug" }, { title: "\xA78Bunker", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "An underground shelter with multiple rooms for survival.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fRoofed Forest Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Roofed Forest Biome\xA7r\n\nTo unlock this structure, discover the Roofed Forest Biome by exploring your world.", id: "unlockable-builds/bunker" }, { title: "\xA75Dragon Head", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A dragon head structure converted into living space with dragon-themed interior.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fDragon Head item\xA7r\n\xA7aUnlock Method:\xA7r \xA7fCraft a Dragon Head item\xA7r\n\nObtain a Dragon Head item, and wear it on your helmet armor slot.", id: "unlockable-builds/dragon-head" }, { title: "\xA75End Portal", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A structure with End dimension architecture and portal design elements.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fDefeat the Ender Dragon\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDefeat the Ender Dragon\xA7r\n\nTo unlock this structure, defeat the Ender Dragon in the End dimension.", id: "unlockable-builds/end-portal" }, { title: "\xA7aFarmers Barn", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A barn with stalls and storage areas for farming operations.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fSavannah Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Savannah Biome\xA7r\n\nTo unlock this structure, discover the Savannah Biome by exploring your world.", id: "unlockable-builds/farmers-barn" }, { title: "\xA7aFarmers Sanctuary", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A structure combining living quarters with farming facilities.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fSavannah Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Savannah Biome\xA7r\n\nDiscover the Savannah Biome to unlock this structure.", id: "unlockable-builds/farmers-sanctuary" }, { title: "\xA7eHunters Watchtower", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A tall watchtower structure with elevated observation areas.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fTaiga Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Taiga Biome\xA7r\n\nDiscover the Taiga Biome to unlock this structure.", id: "unlockable-builds/hunters-watchtower" }, { title: "\xA72Jungle Pyramid", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A pyramid structure with jungle-themed design and hidden chambers.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fJungle Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Jungle Biome\xA7r\n\nDiscover the Jungle Biome to unlock this structure.", id: "unlockable-builds/jungle-pyramid" }, { title: "\xA76Large Pyramid", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A large pyramid structure with multiple chambers and Egyptian-style architecture.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fDesert Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Desert Biome\xA7r\n\nDiscover the Desert Biome to unlock this structure.", id: "unlockable-builds/large-pyramid" }, { title: "\xA75Unlockable Builds", showInSearch: true, buttons: [{ text: "Animal Barn", action: "navigateTo:unlockable-builds/animal-barn", icon: "textures/5fs/cb/items/barn_0_craft" }, { text: "Bunker", action: "navigateTo:unlockable-builds/bunker", icon: "textures/5fs/cb/items/bunker_craft" }, { text: "Farmers Barn", action: "navigateTo:unlockable-builds/farmers-barn", icon: "textures/5fs/cb/items/barn_1_craft" }, { text: "Farmers Sanctuary", action: "navigateTo:unlockable-builds/farmers-sanctuary", icon: "textures/5fs/cb/items/barn_2_craft" }, { text: "Restaurant", action: "navigateTo:unlockable-builds/restaurant", icon: "textures/5fs/cb/items/restaurant_craft" }, { text: "Pyramid", action: "navigateTo:unlockable-builds/pyramid", icon: "textures/5fs/cb/items/pyramid_craft" }, { text: "Hunters Watchtower", action: "navigateTo:unlockable-builds/hunters-watchtower", icon: "textures/5fs/cb/items/watchtower_craft" }, { text: "Large Pyramid", action: "navigateTo:unlockable-builds/large-pyramid", icon: "textures/5fs/cb/items/largepyramid_craft" }, { text: "Jungle Pyramid", action: "navigateTo:unlockable-builds/jungle-pyramid", icon: "textures/5fs/cb/items/junglepyramid_craft" }, { text: "Zombie Hand", action: "navigateTo:unlockable-builds/zombie-hand", icon: "textures/5fs/cb/items/zombiehand_craft" }, { text: "Bedbug", action: "navigateTo:unlockable-builds/bedbug", icon: "textures/5fs/cb/items/bedbug_craft" }, { text: "Dragon Head", action: "navigateTo:unlockable-builds/dragon-head", icon: "textures/5fs/cb/items/dragonhead_craft" }, { text: "Wizards Tower", action: "navigateTo:unlockable-builds/wizards-tower", icon: "textures/5fs/cb/items/wizardhouse_craft" }, { text: "End Portal", action: "navigateTo:unlockable-builds/end-portal", icon: "textures/5fs/cb/items/endportal_craft" }, { text: "Nether Portal", action: "navigateTo:unlockable-builds/nether-portal", icon: "textures/5fs/cb/items/netherportal_craft" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "Structures that must be unlocked by completing achievements, discovering biomes, or obtaining specific items.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fVaries by structure\xA7r\n\xA7aUnlock Method:\xA7r \xA7fBiome discovery, achievements, or special items\xA7r\n\n\xA76Unlock Methods\xA7r\n\n\xA76Biome Discovery\xA7r: Savannah unlocks farming structures, Desert unlocks pyramids, Jungle unlocks temples, Extreme Hills unlock undead builds, Swamps unlock creature-themed structures.\n\n\xA76Achievement Unlocks\xA7r: Defeating the Ender Dragon unlocks End Portal, entering the Nether unlocks Nether Portal.\n\n\xA76Item-Based Unlocks\xA7r: Wearing Dragon Head. unlocks Dragon Head structure, crafting Enchantment Tables unlocks Wizards Tower.", id: "unlockable-builds" }, { title: "\xA7cNether Portal", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A structure with Nether-themed design elements.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fEnter the Nether Dimension\xA7r\n\xA7aUnlock Method:\xA7r \xA7fEnter the Nether Dimension\xA7r\n\nEnter the Nether Dimension to unlock this structure.", id: "unlockable-builds/nether-portal" }, { title: "\xA76Pyramid", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A pyramid structure with chambers and Egyptian-style architecture.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fDesert Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Desert Biome\xA7r\n\nDiscover the Desert Biome to unlock this structure.", id: "unlockable-builds/pyramid" }, { title: "\xA7eRestaurant", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A dining establishment with kitchen facilities and multiple tables.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fBeach/Stony Beach Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Beach/Stony Shore Biome\xA7r\n\nDiscover the Beach or Stony Shore Biome to unlock this structure.", id: "unlockable-builds/restaurant" }, { title: "\xA75Wizards Tower", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A tower structure with rooms for enchanting and magical activities.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fCraft an Enchantment Table\xA7r\n\xA7aUnlock Method:\xA7r \xA7fCraft an Enchantment Table\xA7r\n\nCraft an Enchantment Table to unlock this structure.", id: "unlockable-builds/wizards-tower" }, { title: "\xA78Zombie Hand", showInSearch: true, buttons: [{ text: "Back to Unlockable Builds", action: "navigateTo:unlockable-builds", icon: "textures/ui/arrow_left" }, { text: "Back to Main Menu", action: "navigateTo:main" }], body: "A zombie hand structure converted into living space.\n\n\xA76Craftable:\xA7r \xA7fNo\xA7r\n\xA7bRequirements:\xA7r \xA7fExtreme Hills Biome discovery\xA7r\n\xA7aUnlock Method:\xA7r \xA7fDiscover the Extreme Hills Biome\xA7r\n\nDiscover the Extreme Hills Biome to unlock this structure.", id: "unlockable-builds/zombie-hand" }] };

// data/gametests/src/FurnitureClass.js
import * as mc from "@minecraft/server";

// data/gametests/src/Constants.js
var furnitures = [
  "5fs_cb:door_aquatic_double",
  "5fs_cb:door_bamboo_foldable_glass_double",
  "5fs_cb:door_bat_wing_double",
  "5fs_cb:door_deep_dark_double",
  "5fs_cb:door_ender_dragon_wing",
  "5fs_cb:door_frozen_spruce",
  "5fs_cb:door_oak_glass_double",
  "5fs_cb:door_sandstone_cactus_double",
  "5fs_cb:door_strider"
];
var doors = [
  "5fs_cb:door_aquatic_double",
  "5fs_cb:door_bamboo_foldable_glass_double",
  "5fs_cb:door_bat_wing_double",
  "5fs_cb:door_deep_dark_double",
  "5fs_cb:door_ender_dragon_wing",
  "5fs_cb:door_frozen_spruce",
  "5fs_cb:door_oak_glass_double",
  "5fs_cb:door_sandstone_cactus_double",
  "5fs_cb:door_strider"
];
var barrierBlocks = {
  "5fs_cb:door_aquatic_double": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_bamboo_foldable_glass_double": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_bat_wing_double": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_deep_dark_double": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_ender_dragon_wing": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_frozen_spruce": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_oak_glass_double": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_sandstone_cactus_double": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ],
  "5fs_cb:door_strider": [
    { orientation: 0, xOffSet: 1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 },
    { orientation: 90, xOffSet: 0, yOffSet: 1, zOffSet: 1, xPlus: 0, zPlus: 0 },
    { orientation: 270, xOffSet: 0, yOffSet: 1, zOffSet: -1, xPlus: 0, zPlus: 0 },
    { orientation: 180, xOffSet: -1, yOffSet: 1, zOffSet: 0, xPlus: 0, zPlus: 0 }
  ]
};

// data/gametests/src/FurnitureClass.js
var FurnitureClass = class {
  static async CameraRotate(source, angle = 90, spawn = false) {
    let rotation;
    await this.sleep(1);
    if (spawn) {
      rotation = this.getNormalizedRotation(source);
    } else {
      this.furnitureBlock(source, source.getProperty("5fs_cb:rotation"), "minecraft:air");
      rotation = source.getProperty("5fs_cb:rotation") + angle;
    }
    if (rotation < 0)
      rotation = 270;
    if (rotation >= 360)
      rotation = 0;
    const newRotation = { x: 0, y: rotation };
    source.setRotation(newRotation);
    source.setProperty("5fs_cb:rotation", rotation);
    camerablock(source, rotation);
  }
  static async furnitureRotate(source, angle = 90, spawn = false, block = "minecraft:barrier") {
    let rotation;
    await this.sleep(1);
    if (spawn) {
      rotation = this.getNormalizedRotation(source);
    } else {
      this.furnitureBlock(source, source.getProperty("5fs_cb:rotation"), "minecraft:air");
      rotation = source.getProperty("5fs_cb:rotation") + angle;
    }
    if (rotation < 0)
      rotation = 270;
    if (rotation >= 360)
      rotation = 0;
    const newRotation = { x: 0, y: rotation };
    source.setRotation(newRotation);
    mc.system.runTimeout(() => {
      try {
        this.setLocationAndRotation(source);
      } catch (e) {
      }
    }, 20);
    source.setProperty("5fs_cb:rotation", rotation);
    this.furnitureUpdate(source, rotation, null, block);
    await this.sleep(1);
    this.furnitureBlock(source, rotation, block);
  }
  static furnitureBlock(source, rotation, block = "minecraft:barrier", permutation = {}) {
    let { x, y, z } = source.location;
    const normalizedRotation = rotation;
    const furniture = source.typeId;
    const barrierBlockArray = barrierBlocks[furniture];
    if (!barrierBlockArray) {
      return;
    }
    const barrierObj = barrierBlockArray.find((obj) => Math.abs(obj.orientation - normalizedRotation) < 1);
    if (barrierObj) {
      const { xOffSet, yOffSet, zOffSet, xPlus, zPlus } = barrierObj;
      let targetX = x + xOffSet;
      const targetY = y + yOffSet;
      let targetZ = z + zOffSet;
      if (targetX < x)
        [x, targetX] = [targetX, x];
      if (targetZ < z)
        [z, targetZ] = [targetZ, z];
      this.fillBlock(source, block, x + xPlus, y, z + zPlus, targetX, targetY, targetZ, permutation);
    } else {
    }
  }
  static async furnitureUpdate(source, facing, removeBlock = 0, block = "minecraft:barrier") {
    const { x, y, z } = source.location;
    let xFront = 0, zFront = 0;
    let xLeftSide = 0, zLeftSide = 0;
    let xRightSide = 0, zRightSide = 0;
    switch (facing) {
      case 0:
        zFront = 1;
        xLeftSide = 1;
        xRightSide = -1;
        break;
      case 90:
        xFront = -1;
        zLeftSide = 1;
        zRightSide = -1;
        break;
      case 180:
        zFront = -1;
        xLeftSide = -1;
        xRightSide = 1;
        break;
      case 270:
        xFront = 1;
        zLeftSide = -1;
        zRightSide = 1;
        break;
    }
    const calculateLocation = (xOffset, zOffset) => ({ x: x + xOffset, y, z: z + zOffset });
    const locations = {
      front: calculateLocation(xFront, zFront),
      leftSide: calculateLocation(xLeftSide, zLeftSide),
      rightSide: calculateLocation(xRightSide, zRightSide),
      frontLeftSide: calculateLocation(xLeftSide + xFront, zLeftSide + zFront),
      frontRightSide: calculateLocation(xRightSide + xFront, zRightSide + zFront)
    };
    const testEntityAtLocation = async (location, rotation, isCorner) => {
      let properties = "";
      if (rotation !== void 0 || isCorner !== void 0) {
        properties = `,has_property={`;
        if (rotation !== void 0) {
          properties += `5fs_cb:rotation=${rotation}`;
        }
        if (isCorner !== void 0) {
          properties += (rotation !== void 0 ? "," : "") + `5fs_cb:is_corner=${removeBlock}`;
        }
        properties += "}";
      }
      const command = `testfor @e[type=${source.typeId},x=${location.x},y=${y},z=${location.z},r=0.5${properties}]`;
      const result = await source.runCommand(command);
      return result.successCount > 0;
    };
    try {
      const results = await Promise.all([
        testEntityAtLocation(locations.leftSide),
        testEntityAtLocation(locations.rightSide),
        testEntityAtLocation(locations.frontLeftSide, facing >= 270 ? 0 : facing + 90),
        testEntityAtLocation(locations.frontRightSide, facing <= 0 ? 270 : facing - 90),
        testEntityAtLocation(locations.front, facing >= 270 ? 0 : facing + 90),
        testEntityAtLocation(locations.rightSide, facing),
        testEntityAtLocation(locations.front, facing <= 0 ? 270 : facing - 90),
        testEntityAtLocation(locations.leftSide, facing),
        testEntityAtLocation(locations.leftSide, void 0, 1),
        testEntityAtLocation(locations.rightSide, void 0, 1)
      ]);
      if (results[0] && results[2] && !removeBlock) {
        this.furnitureGetEntity(source, locations.leftSide, async (entity) => {
          try {
            entity.setProperty("5fs_cb:is_corner", 1);
            this.fillBlock(source, "minecraft:air", x, y, z, x, y, z);
            entity.setProperty("5fs_cb:rotation", facing);
            await this.sleep(1);
            this.fillBlock(source, block, x, y, z, x, y, z);
          } catch (e) {
          }
        });
      }
      if (results[1] && results[3] && !removeBlock) {
        this.furnitureGetEntity(source, locations.rightSide, async (entity) => {
          let facing1 = facing <= 0 ? 270 : facing - 90;
          try {
            entity.setProperty("5fs_cb:is_corner", 1);
            this.fillBlock(source, "minecraft:air", x, y, z, x, y, z);
            entity.setProperty("5fs_cb:rotation", facing1);
            await this.sleep(1);
            this.fillBlock(source, block, x, y, z, x, y, z);
          } catch (e) {
          }
        });
      }
      if (results[4] && results[5] && !removeBlock) {
        source.setProperty("5fs_cb:is_corner", 1);
        source.setProperty("5fs_cb:rotation", facing);
      }
      if (results[6] && results[7] && !removeBlock) {
        let facing1 = facing <= 0 ? 270 : facing - 90;
        source.setProperty("5fs_cb:is_corner", 1);
        source.setProperty("5fs_cb:rotation", facing1);
      }
      if (results[8] && removeBlock === 1) {
        this.furnitureGetEntity(source, locations.leftSide, async (entity) => {
          try {
            entity.setProperty("5fs_cb:is_corner", 0);
          } catch (e) {
          }
        });
      }
      if (results[9] && removeBlock === 1) {
        this.furnitureGetEntity(source, locations.rightSide, async (entity) => {
          try {
            entity.setProperty("5fs_cb:is_corner", 0);
          } catch (e) {
          }
        });
      }
    } catch (error) {
    }
  }
  static fillBlock(source, blockPerm, xFrom, yFrom, zFrom, xTo, yTo, zTo, permutation = {}) {
    yFrom = Math.max(-64, yFrom);
    yTo = Math.min(320, yTo);
    for (let i = xFrom; i <= xTo; i++) {
      for (let j = yFrom; j <= yTo; j++) {
        for (let k = zFrom; k <= zTo; k++) {
          const block = source.dimension.getBlock({ x: i, y: j, z: k });
          if (block.permutation.matches("minecraft:air") || block.permutation.matches("minecraft:barrier")) {
            block.setPermutation(mc.BlockPermutation.resolve(blockPerm, permutation));
          }
        }
      }
    }
  }
  static setLocationAndRotation(source) {
    const lAr = {
      locX: source.location.x,
      locY: source.location.y,
      locZ: source.location.z,
      rotX: source.getRotation().x,
      rotY: source.getRotation().y
    };
    const setLocAndRot = JSON.stringify(lAr);
    source.setDynamicProperty("locAndRot", setLocAndRot);
  }
  static furnitureNameTag(source, name = "\xA7l") {
    const newNameTag = name;
    source.nameTag = newNameTag;
  }
  static getNormalizedRotation(source) {
    let view = source.getRotation();
    let roundedRotation = Math.round(view.y / 90) * 90;
    let normalizedRotation = (roundedRotation % 360 + 360) % 360;
    return normalizedRotation;
  }
  static async sleep(ticks) {
    return new Promise((resolve) => mc.system.runTimeout(() => resolve(void 0), ticks));
  }
};
async function camerablock(source, rotation) {
  if (source.typeId === `5fs_cb:barrel_secret_door`) {
    const direction = getCardinalDirection(rotation);
    const block = source.dimension.getBlock(source.location);
    const OpenProperty = source.getProperty(`5fs_cb:open`);
    if (OpenProperty) {
      block.setPermutation(mc.BlockPermutation.resolve("5fs_cb:barrel_secret_door_block", {
        "minecraft:cardinal_direction": direction,
        "5fs_cb:open": true
      }));
    } else {
      block.setPermutation(mc.BlockPermutation.resolve("5fs_cb:barrel_secret_door_block", {
        "minecraft:cardinal_direction": direction,
        "5fs_cb:open": false
      }));
    }
  }
  if (source.typeId === `5fs_cb:haybale_camera`) {
    const direction = getCardinalDirection(rotation);
    const block = source.dimension.getBlock(source.location);
    block.setPermutation(mc.BlockPermutation.resolve("5fs_cb:haybale_camera_block", {
      "minecraft:cardinal_direction": direction
    }));
  } else if (source.typeId === `5fs_cb:stone_camera`) {
    const direction = getCardinalDirection(rotation);
    const block = source.dimension.getBlock(source.location);
    if (block.typeId === `5fs_cb:stone_camera_block`) {
      const texture = block.permutation.getState(`5fs_cb:texture`);
      block.setPermutation(mc.BlockPermutation.resolve("5fs_cb:stone_camera_block", {
        "minecraft:cardinal_direction": direction,
        "5fs_cb:texture": texture
      }));
    } else {
      block.setPermutation(mc.BlockPermutation.resolve("5fs_cb:stone_camera_block", {
        "minecraft:cardinal_direction": direction
      }));
    }
  } else if (source.typeId === `5fs_cb:log_camera`) {
    const direction = getCardinalDirection(rotation);
    const block = source.dimension.getBlock(source.location);
    if (block.typeId === `5fs_cb:log_camera_block`) {
      const texture = block.permutation.getState(`5fs_cb:texture`);
      const stripped = block.permutation.getState(`5fs_cb:stripped_texture`);
      block.setPermutation(mc.BlockPermutation.resolve("5fs_cb:log_camera_block", {
        "minecraft:cardinal_direction": direction,
        "5fs_cb:texture": texture,
        "5fs_cb:stripped_texture": stripped
      }));
    } else {
      block.setPermutation(mc.BlockPermutation.resolve("5fs_cb:log_camera_block", {
        "minecraft:cardinal_direction": direction
      }));
    }
  }
}
function getCardinalDirection(yaw) {
  const rot = (yaw % 360 + 360) % 360;
  if (rot >= 45 && rot < 135)
    return "east";
  if (rot >= 135 && rot < 225)
    return "south";
  if (rot >= 225 && rot < 315)
    return "west";
  return "north";
}
mc.world.afterEvents.entitySpawn.subscribe(({ entity, cause }) => {
  if (cause === "Spawned") {
    try {
      if (!furnitures.includes(entity.typeId))
        return;
      if (doors.includes(entity.typeId)) {
        FurnitureClass.furnitureRotate(entity, null, true);
      }
      FurnitureClass.furnitureNameTag(entity);
    } catch (error) {
    }
  }
});
mc.system.afterEvents.scriptEventReceive.subscribe(({ id, initiator, message, sourceBlock, sourceEntity, sourceType }) => {
  let closeOpenProperty;
  switch (id) {
    case `5fs_cb:furniture.rotate`:
      if (!furnitures.includes(sourceEntity.typeId))
        return;
      else {
        closeOpenProperty = sourceEntity.getProperty("5fs_cb:close_open");
        if (closeOpenProperty) {
          FurnitureClass.furnitureRotate(sourceEntity, 90, false, "minecraft:air");
        } else {
          if (doors.includes(sourceEntity.typeId)) {
            FurnitureClass.furnitureRotate(sourceEntity, 90, false);
          } else {
            FurnitureClass.furnitureRotate(sourceEntity, 90, false);
          }
        }
      }
      break;
    case "5fs_cb:furniture.remove":
      FurnitureClass.furnitureBlock(sourceEntity, sourceEntity.getProperty("5fs_cb:rotation"), "minecraft:air");
      break;
    case "5fs_cb:furniture.open_close":
      closeOpenProperty = sourceEntity.getProperty("5fs_cb:close_open");
      if (closeOpenProperty) {
        FurnitureClass.furnitureBlock(sourceEntity, sourceEntity.getProperty("5fs_cb:rotation"), "minecraft:air");
      } else {
        FurnitureClass.furnitureBlock(sourceEntity, sourceEntity.getProperty("5fs_cb:rotation"), "minecraft:barrier");
      }
      break;
  }
});

// data/gametests/src/index.ts
var guidebook = new Guidebook(guidebook_data_default, {
  logLevel: "error"
});
guidebook.init();
var LORE_PROCESSED_MARKER = "\xA7r\xA7r\xA7l\xA7o\xA7r\xA7e";
system17.afterEvents.scriptEventReceive.subscribe(({ sourceEntity, id }) => {
  if (id === "5fs_cb:open_guidebook") {
    guidebook.open(sourceEntity);
  }
});
function wrapText(text, maxChars = 40) {
  const words = text.split(" ");
  const lines = [];
  let currentLine = "";
  lines.push("\xA7r\xA71Craftable Bases Add-On");
  for (const word of words) {
    if (currentLine.length + word.length + (currentLine ? 1 : 0) <= maxChars) {
      currentLine += (currentLine ? " " : "") + word;
    } else {
      if (currentLine.length) {
        lines.push(`\xA7r\xA73${currentLine}`);
      }
      currentLine = word;
    }
  }
  if (currentLine.length) {
    lines.push(`\xA7r\xA73${currentLine}`);
  }
  return lines;
}
var tools = [
  {
    item: "5fs_cb:guidebook",
    name: "Guidebook",
    texture: "textures/5fs/modern_security/items/",
    lore: ["Press use on the guidebook to learn more about Craftable Bases Add-On"]
  },
  {
    item: "5fs_cb:ruler",
    name: "Ruler",
    texture: "textures/5fs/modern_security/items/",
    lore: ["Press use on doors and tables to center them"]
  },
  {
    item: "5fs_cb:sledgehammer",
    name: "Sledgehammer",
    texture: "textures/5fs/modern_security/items/",
    lore: ["Press use on furniture to destroy it"]
  },
  {
    item: "5fs_cb:wrench",
    name: "Wrench",
    texture: "textures/5fs/modern_security/items/",
    lore: ["Press use on furniture to rotate it"]
  }
];
system17.runInterval(() => {
  for (const player of world15.getPlayers()) {
    const invComp = player.getComponent("minecraft:inventory");
    const container = invComp.container;
    for (let i = 0; i < container.size; i++) {
      const invItem = container.getItem(i);
      if (!invItem)
        continue;
      const existingLore = invItem.getLore() ?? [];
      if (existingLore.includes(LORE_PROCESSED_MARKER)) {
        if (invItem.typeId === "5fs_cb:restore_terrain") {
          const updatedItem = expireItem(player, invItem, 1);
          container.setItem(i, updatedItem);
        }
        continue;
      }
      const toolEntry = tools.find((tool) => tool.item === invItem.typeId);
      const craftEntry = craftList.find((build) => build.item === invItem.typeId);
      let loreWasUpdated = false;
      if (craftEntry) {
        const wrappedLore = wrapText(craftEntry.lore, 40);
        invItem.setLore(wrappedLore);
        loreWasUpdated = true;
      } else if (toolEntry) {
        let newLore = [...existingLore];
        toolEntry.lore.forEach((loreLine) => {
          const wrappedToolLore = wrapText(loreLine, 40);
          wrappedToolLore.forEach((line) => {
            if (!newLore.includes(line)) {
              newLore.push(line);
            }
          });
        });
        invItem.setLore(newLore);
        loreWasUpdated = true;
      }
      if (loreWasUpdated) {
        const finalLore = invItem.getLore() ?? [];
        finalLore.push(LORE_PROCESSED_MARKER);
        invItem.setLore(finalLore);
        container.setItem(i, invItem);
      }
      if (invItem.typeId === "minecraft:enchanting_table" && !player.hasTag("enchant_table_recipe")) {
        player.runCommand("give @s[tag=!world_init,tag=!enchant_table_recipe] 5fs_cb:wizardhouse_craft 1"), player.runCommand("recipe give @s[tag=!world_init,tag=!enchant_table_recipe] 5fs_cb:small_tower_recipe"), player.runCommand('tellraw @s[tag=!world_init,tag=!enchant_table_recipe] {"rawtext":[{"text":"\xA7l[\xA7b!\xA7r\xA7l]\xA7r \xA7rNew Discovery: Enchanting! For crafting a \xA7lEnchantment Table\xA7r you have unlocked the mystical \xA7lWizards Tower\xA7r. This structure has been given to you."}]}'), player.runCommand("tag @s add enchant_table_recipe");
      }
      if (invItem.typeId === "5fs_cb:restore_terrain") {
        const updatedItem = expireItem(player, invItem, 1);
        container.setItem(i, updatedItem);
      }
    }
  }
}, 20);
