# Rigacar (Blender 4.2 – 5.1+ Edition)

[![Blender Version](https://img.shields.io/badge/Blender-4.2%20--%205.1%2B-orange.svg)](https://www.blender.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A maintained, enhanced fork of **Rigacar** updated and optimized for **Blender 4.2, 5.0, and 5.1+**.

Rigacar quickly generates complete vehicle animation rigs with automated wheel rotation, suspension dynamics, ground projection, and animation baking.

---

## 🚀 What's New in this Edition

* **Full Blender 5.1+ Compatibility:**
  * Updated to use Blender's new **Slotted Actions / `ActionChannelbag` API** (legacy `action.fcurves` deprecation fix).
  * Migrated from legacy layers to **Bone Collections** (`CarRig_Default_Ctrls`, `CarRig_Def_Bone`, etc.).
  * Validated for Blender's new **Extensions Manager** (`blender_manifest.toml`).
* **Interactive Car Parts Setup (N-Panel):**
  * Dedicated **Car Parts Setup** view in the 3D Viewport sidebar (**Rigacar** tab).
  * **Auto-Detect Parts:** Intelligently matches Body, 4 Wheels, Brakes, Doors, Trunk, Hood, and Windows from selected or scene objects.
  * **One-Click Rig Generation & Snapping:** Perfectly scales and positions bone hierarchies to match your chosen 3D meshes with zero guesswork.
* **Interactive Doors, Windows, Trunk & Hood:**
  * **Door Hinge Rigging:** Automatic detection of door hinge pivots (prioritizing custom mesh origins and calculating front door seams without side-mirror distortion).
  * **Dedicated Window Bones:** Window panes get dedicated animatable bones parented to their doors (`Window.Ft.L` -> `Door.Ft.L`), allowing realistic roll-down animation inside the door frame while swinging open together with the door.
  * **Trunk & Hood:** Horizontal hinge bones for hoods and tailgates.
* **Preserved Transform Safety:**
  * Re-snapping or modifying bones safely preserves world matrices, preventing parented meshes from drifting or jumping.

---

## 📦 Installation

### Option A: Install from Zip (Blender 4.2 / 5.x)
1. Download **`rigacar-1.0.4.zip`** from the [Releases](https://github.com/lukaiaa/rigacar-Blender-5.0-/releases) page.
2. In Blender, go to **Edit → Preferences → Add-ons / Extensions**.
3. Click the dropdown menu in the upper-right corner (arrow icon) and choose **Install from Disk...**.
4. Select `rigacar-1.0.4.zip` and enable **Rigacar**.

---

## 🛠️ Quick Start Guide

1. Open the 3D Viewport sidebar (press `N`) and click the **Rigacar** tab.
2. Under **Car Parts Setup**:
   * Click **Auto-Detect Parts** (or assign your meshes using the eyedroppers).
   * Toggle **Doors**, **Hood & Trunk**, or **Windows & Glass** if your vehicle has separate parts.
3. Click **Create Rig from Chosen Parts** (or **Snap Bones to Chosen Parts** if you already added a deformation rig).
4. Click **Attach Parts to Rig** to parent all meshes with preserved world positions.
5. Click **Generate Animation Rig**.
6. Switch to **Pose Mode** to animate:
   * Move the **Root** bone to drive the vehicle.
   * Rotate **Door.Ft.L** / **Door.Ft.R** along Z to open doors.
   * Move **Window.Ft.L** / **Window.Ft.R** along Z to roll down windows.
   * Rotate **Trunk** / **Hood** along X to open.
   * In the Rigacar panel, click **Bake wheels rotation** to bake automatic wheel spinning.

---

## 🎮 Exporting to Game Engines (Unity / Unreal Engine)

1. Select your car meshes and armature.
2. Go to **File → Export → FBX (.fbx)**.
3. In the export settings:
   * **Include:** Check *Selected Objects*, select *Armature* and *Mesh*.
   * **Armature:**
     * ✅ Check **Only Deform Bones** (strips out control widgets, leaving only the clean deform skeleton).
     * ❌ Uncheck **Add Leaf Bones** (prevents unnecessary `_end` dummy bones).
   * **Animation:**
     * If playing animations in Unity/Unreal, bake the action first via **Pose → Animation → Bake Action...** (enable *Visual Keying*) since game engines do not execute Blender constraints.
     * If using game engine vehicle physics (e.g. Unity `WheelCollider`), export in default rest pose without animation.

---

## 📜 Credits & License

* Originally created by **David Gayerie** ([digicreatures.net](http://digicreatures.net/articles/rigacar.html)).
* Maintained and extended by the community under the **GNU General Public License v3 (GPL-3.0)**.
