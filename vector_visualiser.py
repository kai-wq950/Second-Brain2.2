"""
A-Level Edexcel Core Pure 1 & 2 vector visualiser.
Single-file Tkinter application using Matplotlib for 2D/3D plotting.
"""
import math
import re
from dataclasses import dataclass
from typing import List, Tuple

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 - side effect import
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------------
# Utility parsing helpers
# ---------------------------

def parse_numbers(text: str) -> List[float]:
    """Parse a comma/space separated list of numbers from text like "1,2,3" or "(1 2 3)"."""
    cleaned = text.strip().replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    parts = re.split(r"[ ,;]+", cleaned)
    numbers = []
    for part in parts:
        if not part:
            continue
        numbers.append(float(part))
    return numbers


def parse_vector(text: str, dim: int) -> List[float]:
    """Parse vectors given as components or ijk form."""
    cleaned = text.replace(" ", "")
    ijk_match = re.findall(r"([+-]?\d*\.?\d*)i|([+-]?\d*\.?\d*)j|([+-]?\d*\.?\d*)k", cleaned)
    if ijk_match:
        i_val = j_val = k_val = 0.0
        for groups in ijk_match:
            if groups[0]:
                i_val = float(groups[0] or 0)
            if groups[1]:
                j_val = float(groups[1] or 0)
            if groups[2]:
                k_val = float(groups[2] or 0)
        components = [i_val, j_val]
        if dim == 3:
            components.append(k_val)
        return components
    numbers = parse_numbers(text)
    if len(numbers) != dim:
        raise ValueError(f"Expected {dim} components, got {numbers}")
    return numbers


# ---------------------------
# Core maths classes
# ---------------------------

@dataclass
class Vector2D:
    x: float
    y: float

    @classmethod
    def from_text(cls, text: str) -> "Vector2D":
        x, y = parse_vector(text, 2)
        return cls(x, y)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)

    # Operations
    def magnitude(self) -> float:
        return float(np.linalg.norm(self.to_array()))

    def unit(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Zero vector has no direction")
        arr = self.to_array() / mag
        return Vector2D(*arr)

    def add(self, other: "Vector2D") -> "Vector2D":
        arr = self.to_array() + other.to_array()
        return Vector2D(*arr)

    def subtract(self, other: "Vector2D") -> "Vector2D":
        arr = self.to_array() - other.to_array()
        return Vector2D(*arr)

    def scale(self, k: float) -> "Vector2D":
        arr = self.to_array() * k
        return Vector2D(*arr)

    def dot(self, other: "Vector2D") -> float:
        return float(np.dot(self.to_array(), other.to_array()))

    def angle_with(self, other: "Vector2D") -> float:
        denom = self.magnitude() * other.magnitude()
        if denom == 0:
            raise ValueError("Angle undefined for zero vector")
        cos_theta = np.clip(self.dot(other) / denom, -1.0, 1.0)
        return math.degrees(math.acos(cos_theta))

    def projection_on(self, other: "Vector2D") -> "Vector2D":
        if other.magnitude() == 0:
            raise ValueError("Cannot project onto zero vector")
        scalar = self.dot(other) / other.dot(other)
        return other.scale(scalar)

    def __str__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f})"


@dataclass
class Vector3D:
    x: float
    y: float
    z: float

    @classmethod
    def from_text(cls, text: str) -> "Vector3D":
        x, y, z = parse_vector(text, 3)
        return cls(x, y, z)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)

    def magnitude(self) -> float:
        return float(np.linalg.norm(self.to_array()))

    def unit(self) -> "Vector3D":
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Zero vector has no direction")
        arr = self.to_array() / mag
        return Vector3D(*arr)

    def add(self, other: "Vector3D") -> "Vector3D":
        arr = self.to_array() + other.to_array()
        return Vector3D(*arr)

    def subtract(self, other: "Vector3D") -> "Vector3D":
        arr = self.to_array() - other.to_array()
        return Vector3D(*arr)

    def scale(self, k: float) -> "Vector3D":
        arr = self.to_array() * k
        return Vector3D(*arr)

    def dot(self, other: "Vector3D") -> float:
        return float(np.dot(self.to_array(), other.to_array()))

    def cross(self, other: "Vector3D") -> "Vector3D":
        cross_arr = np.cross(self.to_array(), other.to_array())
        return Vector3D(*cross_arr)

    def angle_with(self, other: "Vector3D") -> float:
        denom = self.magnitude() * other.magnitude()
        if denom == 0:
            raise ValueError("Angle undefined for zero vector")
        cos_theta = np.clip(self.dot(other) / denom, -1.0, 1.0)
        return math.degrees(math.acos(cos_theta))

    def projection_on(self, other: "Vector3D") -> "Vector3D":
        if other.magnitude() == 0:
            raise ValueError("Cannot project onto zero vector")
        scalar = self.dot(other) / other.dot(other)
        return other.scale(scalar)

    def __str__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


# ---------------------------
# Geometry classes
# ---------------------------

@dataclass
class Line2D:
    point: Vector2D
    direction: Vector2D

    @classmethod
    def from_cartesian(cls, a: float, b: float, c: float) -> "Line2D":
        # Use point when y=0 -> x = -c/a if possible else x=0 -> y=-c/b
        if abs(a) > 1e-9:
            point = Vector2D(-c / a, 0)
        else:
            point = Vector2D(0, -c / b)
        direction = Vector2D(b, -a)
        return cls(point, direction)

    def to_cartesian(self) -> Tuple[float, float, float]:
        a = -self.direction.y
        b = self.direction.x
        c = -(a * self.point.x + b * self.point.y)
        return a, b, c

    def parametric(self) -> Tuple[float, float, float, float]:
        return self.point.x, self.direction.x, self.point.y, self.direction.y

    def point_at(self, lam: float) -> Vector2D:
        arr = self.point.to_array() + lam * self.direction.to_array()
        return Vector2D(*arr)

    def __str__(self) -> str:
        return f"r = ({self.point.x:.2f},{self.point.y:.2f}) + λ({self.direction.x:.2f},{self.direction.y:.2f})"


@dataclass
class Line3D:
    point: Vector3D
    direction: Vector3D

    @classmethod
    def from_symmetric(cls, x1: float, y1: float, z1: float, l: float, m: float, n: float) -> "Line3D":
        return cls(Vector3D(x1, y1, z1), Vector3D(l, m, n))

    def parametric(self) -> Tuple[float, float, float, float, float, float]:
        return (
            self.point.x,
            self.direction.x,
            self.point.y,
            self.direction.y,
            self.point.z,
            self.direction.z,
        )

    def symmetric(self) -> Tuple[float, float, float, float, float, float]:
        return self.point.x, self.point.y, self.point.z, self.direction.x, self.direction.y, self.direction.z

    def point_at(self, lam: float) -> Vector3D:
        arr = self.point.to_array() + lam * self.direction.to_array()
        return Vector3D(*arr)

    def __str__(self) -> str:
        p = self.point
        d = self.direction
        return f"r = ({p.x:.2f},{p.y:.2f},{p.z:.2f}) + λ({d.x:.2f},{d.y:.2f},{d.z:.2f})"


@dataclass
class Plane3D:
    a: float
    b: float
    c: float
    d: float

    @classmethod
    def from_point_normal(cls, point: Vector3D, normal: Vector3D) -> "Plane3D":
        a, b, c = normal.to_array()
        d = -(a * point.x + b * point.y + c * point.z)
        return cls(a, b, c, d)

    def normal(self) -> Vector3D:
        return Vector3D(self.a, self.b, self.c)

    def point_on_plane(self) -> Vector3D:
        if abs(self.c) > 1e-9:
            return Vector3D(0, 0, -self.d / self.c)
        if abs(self.b) > 1e-9:
            return Vector3D(0, -self.d / self.b, 0)
        return Vector3D(-self.d / self.a, 0, 0)

    def vector_form(self) -> Tuple[Vector3D, Vector3D, Vector3D]:
        p = self.point_on_plane()
        n = self.normal().to_array()
        # choose two non-parallel direction vectors
        if abs(n[2]) > 1e-9:
            d1 = np.array([1, 0, -n[0] / n[2]])
            d2 = np.array([0, 1, -n[1] / n[2]])
        elif abs(n[1]) > 1e-9:
            d1 = np.array([1, -n[0] / n[1], 0])
            d2 = np.array([0, 0, 1])
        else:
            d1 = np.array([0, 1, 0])
            d2 = np.array([0, 0, 1])
        return p, Vector3D(*d1), Vector3D(*d2)

    def __str__(self) -> str:
        return f"{self.a:.2f}x + {self.b:.2f}y + {self.c:.2f}z + {self.d:.2f} = 0"


# ---------------------------
# GUI application
# ---------------------------

class VisualiserApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("A-Level Vector Visualiser (Edexcel CP1 & CP2)")
        root.geometry("1200x700")

        self.objects = []  # list of tuples (name, obj_type, dim, obj)
        self.counter = {"Vector": 1, "Point": 1, "Line": 1, "Plane": 1}

        self._build_ui()
        self._setup_plot()

    # UI construction
    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.left = ttk.Frame(main_frame, width=350)
        self.left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.right = ttk.Frame(main_frame)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Inputs
        ttk.Label(self.left, text="Object type").pack(anchor=tk.W)
        self.object_type = tk.StringVar(value="Vector")
        ttk.Combobox(self.left, textvariable=self.object_type, values=["Vector", "Point", "Line", "Plane"], state="readonly").pack(fill=tk.X)

        ttk.Label(self.left, text="Dimension (where relevant)").pack(anchor=tk.W, pady=(10, 0))
        self.dimension = tk.StringVar(value="3D")
        ttk.Combobox(self.left, textvariable=self.dimension, values=["2D", "3D"], state="readonly").pack(fill=tk.X)

        ttk.Label(self.left, text="Input form").pack(anchor=tk.W, pady=(10, 0))
        self.form_choice = tk.StringVar(value="Vector (components)")
        self.form_box = ttk.Combobox(self.left, textvariable=self.form_choice, values=self._form_options(), state="readonly")
        self.form_box.pack(fill=tk.X)

        self.object_type.trace_add("write", self._update_form_choices)
        self.dimension.trace_add("write", self._update_form_choices)

        ttk.Label(self.left, text="Parameters (comma separated)").pack(anchor=tk.W, pady=(10, 0))
        self.input_entry = tk.Entry(self.left)
        self.input_entry.pack(fill=tk.X)
        ttk.Label(self.left, text="Examples shown below:").pack(anchor=tk.W)
        self.example_label = ttk.Label(self.left, text=self._example_text(), wraplength=320, foreground="gray")
        self.example_label.pack(anchor=tk.W)

        ttk.Button(self.left, text="Add object", command=self.add_object).pack(fill=tk.X, pady=(10, 0))
        ttk.Button(self.left, text="Clear all", command=self.clear_all).pack(fill=tk.X, pady=2)

        ttk.Separator(self.left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(self.left, text="Operations").pack(anchor=tk.W)
        self.obj1_var = tk.StringVar()
        self.obj2_var = tk.StringVar()
        self.operation_var = tk.StringVar()

        self.obj1_combo = ttk.Combobox(self.left, textvariable=self.obj1_var, values=[])
        self.obj2_combo = ttk.Combobox(self.left, textvariable=self.obj2_var, values=[])
        self.operation_combo = ttk.Combobox(self.left, textvariable=self.operation_var, values=self._operation_options(), state="readonly")

        ttk.Label(self.left, text="First object").pack(anchor=tk.W)
        self.obj1_combo.pack(fill=tk.X)
        ttk.Label(self.left, text="Second object (if needed)").pack(anchor=tk.W)
        self.obj2_combo.pack(fill=tk.X)
        ttk.Label(self.left, text="Choose operation").pack(anchor=tk.W)
        self.operation_combo.pack(fill=tk.X)

        ttk.Label(self.left, text="Scalar (for scaling)").pack(anchor=tk.W, pady=(10, 0))
        self.scalar_entry = tk.Entry(self.left)
        self.scalar_entry.pack(fill=tk.X)

        ttk.Button(self.left, text="Compute", command=self.compute_operation).pack(fill=tk.X, pady=(10, 0))

        # Results panel
        self.results_text = tk.Text(self.right, height=12, wrap=tk.WORD)
        self.results_text.pack(fill=tk.X, padx=5, pady=5)

    def _setup_plot(self):
        self.fig = Figure(figsize=(6, 5))
        self.ax2d = self.fig.add_subplot(121)
        self.ax3d = self.fig.add_subplot(122, projection="3d")
        self.ax2d.set_title("2D view")
        self.ax3d.set_title("3D view")
        self.ax2d.grid(True)
        self.ax3d.grid(True)
        self.ax2d.set_xlim(-6, 6)
        self.ax2d.set_ylim(-6, 6)
        self.ax3d.set_xlim(-6, 6)
        self.ax3d.set_ylim(-6, 6)
        self.ax3d.set_zlim(-6, 6)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self.right)
        toolbar.update()

    # ---------------------------
    # Helper methods
    # ---------------------------
    def _form_options(self) -> List[str]:
        obj = self.object_type.get()
        dim = self.dimension.get()
        if obj == "Vector":
            return ["Vector (components)", "Vector (i, j, k)"]
        if obj == "Point":
            return ["Point (coordinates)"]
        if obj == "Line":
            if dim == "2D":
                return ["Line – vector form", "Line – Cartesian (ax + by + c = 0)"]
            else:
                return ["Line – vector form", "Line – symmetric"]
        if obj == "Plane":
            return ["Plane – Cartesian", "Plane – point & normal"]
        return []

    def _example_text(self) -> str:
        obj = self.object_type.get()
        dim = self.dimension.get()
        if obj == "Vector":
            return "Example: (1,2,3) or 1,2,3 or 2i-3j+k"
        if obj == "Point":
            return "Example: (3, -1, 2)"
        if obj == "Line" and dim == "2D":
            return "Vector form: x0,y0,l,m -> e.g. 1,2,3,1. Cartesian: a,b,c"
        if obj == "Line" and dim == "3D":
            return "Vector form: x0,y0,z0,l,m,n. Symmetric: x1,y1,z1,l,m,n"
        if obj == "Plane":
            return "Cartesian: a,b,c,d. Point & normal: x0,y0,z0,nx,ny,nz"
        return ""

    def _operation_options(self) -> List[str]:
        return [
            "Magnitude (vector)",
            "Unit vector",
            "Add vectors",
            "Subtract vectors",
            "Scalar multiply",
            "Dot product",
            "Angle between vectors",
            "Cross product (3D)",
            "Distance between points",
            "Point to line distance",
            "Point to plane distance",
            "Line-Line intersection (2D)",
            "Line-Plane intersection (3D)",
        ]

    def _update_form_choices(self, *_):
        options = self._form_options()
        self.form_box["values"] = options
        if options:
            self.form_choice.set(options[0])
        self.example_label.config(text=self._example_text())

    def _update_object_combos(self):
        names = [name for name, _, _, _ in self.objects]
        self.obj1_combo["values"] = names
        self.obj2_combo["values"] = names

    def log(self, text: str):
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)

    # ---------------------------
    # Object creation
    # ---------------------------
    def add_object(self):
        obj_type = self.object_type.get()
        dim = self.dimension.get()
        form = self.form_choice.get()
        raw = self.input_entry.get()

        try:
            if obj_type == "Vector":
                if dim == "2D":
                    v = Vector2D.from_text(raw)
                else:
                    v = Vector3D.from_text(raw)
                name = f"v{self.counter['Vector']}"
                self.counter["Vector"] += 1
                self.objects.append((name, "Vector", dim, v))
                self.log(f"Added vector {name} = {v}")
                self.log(f"Magnitude |{name}| = {v.magnitude():.3f}")
                if isinstance(v, Vector2D):
                    self.log(f"i,j form: {v.x:.2f}i + {v.y:.2f}j")
                else:
                    self.log(f"i,j,k form: {v.x:.2f}i + {v.y:.2f}j + {v.z:.2f}k")

            elif obj_type == "Point":
                nums = parse_numbers(raw)
                if dim == "2D" and len(nums) == 2:
                    p = Vector2D(*nums)
                elif dim == "3D" and len(nums) == 3:
                    p = Vector3D(*nums)
                else:
                    raise ValueError("Point needs 2 or 3 coordinates")
                name = f"P{self.counter['Point']}"
                self.counter["Point"] += 1
                self.objects.append((name, "Point", dim, p))
                self.log(f"Added point {name} = {p}")

            elif obj_type == "Line":
                if dim == "2D":
                    if "Cartesian" in form:
                        a, b, c = parse_numbers(raw)
                        line = Line2D.from_cartesian(a, b, c)
                    else:
                        x0, y0, l, m = parse_numbers(raw)
                        line = Line2D(Vector2D(x0, y0), Vector2D(l, m))
                    name = f"L{self.counter['Line']}"
                    self.counter["Line"] += 1
                    self.objects.append((name, "Line", dim, line))
                    a, b, c = line.to_cartesian()
                    self.log(f"Added line {name}: {line}")
                    self.log(f"Cartesian: {a:.2f}x + {b:.2f}y + {c:.2f} = 0")
                    px, dx, py, dy = line.parametric()
                    self.log(f"Parametric: x={px:.2f}+λ{dx:.2f}, y={py:.2f}+λ{dy:.2f}")
                else:  # 3D
                    if "symmetric" in form.lower():
                        x1, y1, z1, l, m, n = parse_numbers(raw)
                        line = Line3D.from_symmetric(x1, y1, z1, l, m, n)
                    else:
                        x0, y0, z0, l, m, n = parse_numbers(raw)
                        line = Line3D(Vector3D(x0, y0, z0), Vector3D(l, m, n))
                    name = f"L{self.counter['Line']}"
                    self.counter["Line"] += 1
                    self.objects.append((name, "Line", dim, line))
                    self.log(f"Added line {name}: {line}")
                    px, dx, py, dy, pz, dz = line.parametric()
                    self.log(f"Parametric: x={px:.2f}+λ{dx:.2f}, y={py:.2f}+λ{dy:.2f}, z={pz:.2f}+λ{dz:.2f}")
                    sx, sy, sz, l, m, n = line.symmetric()
                    self.log(f"Symmetric: (x-{sx:.2f})/{l:.2f} = (y-{sy:.2f})/{m:.2f} = (z-{sz:.2f})/{n:.2f}")

            elif obj_type == "Plane":
                if "Cartesian" in form:
                    a, b, c, d = parse_numbers(raw)
                    plane = Plane3D(a, b, c, d)
                else:
                    x0, y0, z0, nx, ny, nz = parse_numbers(raw)
                    plane = Plane3D.from_point_normal(Vector3D(x0, y0, z0), Vector3D(nx, ny, nz))
                name = f"Π{self.counter['Plane']}"
                self.counter["Plane"] += 1
                self.objects.append((name, "Plane", "3D", plane))
                self.log(f"Added plane {name}: {plane}")
                p, d1, d2 = plane.vector_form()
                self.log(
                    f"Vector form: r = ({p.x:.2f},{p.y:.2f},{p.z:.2f}) + λ({d1.x:.2f},{d1.y:.2f},{d1.z:.2f}) + μ({d2.x:.2f},{d2.y:.2f},{d2.z:.2f})"
                )
                n = plane.normal()
                self.log(f"Normal vector: {n}")
            else:
                raise ValueError("Unsupported object type")
        except Exception as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        self._update_object_combos()
        self.update_plot()

    def clear_all(self):
        self.objects.clear()
        self.results_text.delete("1.0", tk.END)
        self.counter = {"Vector": 1, "Point": 1, "Line": 1, "Plane": 1}
        self._update_object_combos()
        self.update_plot()

    # ---------------------------
    # Operations
    # ---------------------------
    def _get_object(self, name: str):
        for n, t, d, obj in self.objects:
            if n == name:
                return n, t, d, obj
        raise ValueError("Unknown object")

    def compute_operation(self):
        op = self.operation_var.get()
        try:
            if op in ["Magnitude (vector)", "Unit vector"]:
                name = self.obj1_var.get()
                _, t, _, obj = self._get_object(name)
                if t != "Vector":
                    raise ValueError("Choose a vector")
                if op == "Magnitude (vector)":
                    mag = obj.magnitude()
                    self.log(f"|{name}| = {mag:.3f}")
                else:
                    unit = obj.unit()
                    self.log(f"Unit vector of {name} = {unit}")

            elif op in ["Add vectors", "Subtract vectors", "Dot product", "Angle between vectors", "Cross product (3D)"]:
                n1 = self.obj1_var.get()
                n2 = self.obj2_var.get()
                _, t1, _, v1 = self._get_object(n1)
                _, t2, _, v2 = self._get_object(n2)
                if t1 != "Vector" or t2 != "Vector":
                    raise ValueError("Pick two vectors")
                if op == "Add vectors":
                    res = v1.add(v2)
                    self.log(f"{n1} + {n2} = {res}")
                elif op == "Subtract vectors":
                    res = v1.subtract(v2)
                    self.log(f"{n1} - {n2} = {res}")
                elif op == "Dot product":
                    val = v1.dot(v2)
                    self.log(f"{n1} · {n2} = {val:.3f}")
                elif op == "Angle between vectors":
                    angle = v1.angle_with(v2)
                    self.log(f"Angle between {n1} and {n2} = {angle:.2f}°")
                else:
                    if not isinstance(v1, Vector3D) or not isinstance(v2, Vector3D):
                        raise ValueError("Cross product only for 3D vectors")
                    res = v1.cross(v2)
                    self.log(f"{n1} × {n2} = {res}")

            elif op == "Scalar multiply":
                name = self.obj1_var.get()
                scalar = float(self.scalar_entry.get())
                _, t, _, obj = self._get_object(name)
                if t != "Vector":
                    raise ValueError("Choose a vector")
                res = obj.scale(scalar)
                self.log(f"{scalar:.2f} × {name} = {res}")

            elif op == "Distance between points":
                n1 = self.obj1_var.get()
                n2 = self.obj2_var.get()
                _, t1, _, p1 = self._get_object(n1)
                _, t2, _, p2 = self._get_object(n2)
                if t1 != "Point" or t2 != "Point":
                    raise ValueError("Pick two points")
                arr1 = np.array([p1.x, p1.y] if isinstance(p1, Vector2D) else [p1.x, p1.y, p1.z])
                arr2 = np.array([p2.x, p2.y] if isinstance(p2, Vector2D) else [p2.x, p2.y, p2.z])
                dist = np.linalg.norm(arr1 - arr2)
                self.log(f"Distance {n1}{n2} = {dist:.3f}")

            elif op == "Point to line distance":
                p_name = self.obj1_var.get()
                l_name = self.obj2_var.get()
                _, t1, d1, point = self._get_object(p_name)
                _, t2, d2, line = self._get_object(l_name)
                if t1 != "Point" or t2 != "Line":
                    raise ValueError("Select a point then a line")
                if d2 == "2D":
                    if not isinstance(point, Vector2D):
                        raise ValueError("Point and line dimension mismatch")
                    a, b, c = line.to_cartesian()
                    dist = abs(a * point.x + b * point.y + c) / math.hypot(a, b)
                else:
                    p = np.array([point.x, point.y, point.z])
                    p0 = line.point.to_array()
                    d = line.direction.to_array()
                    dist = np.linalg.norm(np.cross(p - p0, d)) / np.linalg.norm(d)
                self.log(f"Distance from {p_name} to {l_name} = {dist:.3f}")

            elif op == "Point to plane distance":
                p_name = self.obj1_var.get()
                pl_name = self.obj2_var.get()
                _, t1, _, point = self._get_object(p_name)
                _, t2, _, plane = self._get_object(pl_name)
                if t1 != "Point" or t2 != "Plane":
                    raise ValueError("Select a point and a plane")
                if not isinstance(point, Vector3D):
                    raise ValueError("Plane is 3D; point must be 3D")
                num = abs(plane.a * point.x + plane.b * point.y + plane.c * point.z + plane.d)
                den = math.sqrt(plane.a ** 2 + plane.b ** 2 + plane.c ** 2)
                self.log(f"Distance from {p_name} to {pl_name} = {num/den:.3f}")

            elif op == "Line-Line intersection (2D)":
                l1 = self.obj1_var.get()
                l2 = self.obj2_var.get()
                _, t1, d1, line1 = self._get_object(l1)
                _, t2, d2, line2 = self._get_object(l2)
                if t1 != "Line" or t2 != "Line" or d1 != "2D" or d2 != "2D":
                    raise ValueError("Pick two 2D lines")
                a1, b1, c1 = line1.to_cartesian()
                a2, b2, c2 = line2.to_cartesian()
                det = a1 * b2 - a2 * b1
                if abs(det) < 1e-9:
                    self.log(f"{l1} and {l2} are parallel or coincident")
                else:
                    x = (b1 * c2 - b2 * c1) / det
                    y = (c1 * a2 - c2 * a1) / det
                    self.log(f"Intersection of {l1} and {l2}: ({x:.2f}, {y:.2f})")

            elif op == "Line-Plane intersection (3D)":
                l_name = self.obj1_var.get()
                p_name = self.obj2_var.get()
                _, t1, d1, line = self._get_object(l_name)
                _, t2, _, plane = self._get_object(p_name)
                if t1 != "Line" or d1 != "3D" or t2 != "Plane":
                    raise ValueError("Choose a 3D line and a plane")
                p0 = line.point.to_array()
                d = line.direction.to_array()
                n = plane.normal().to_array()
                denom = np.dot(n, d)
                if abs(denom) < 1e-9:
                    self.log(f"{l_name} is parallel to {p_name}")
                else:
                    t_param = -(np.dot(n, p0) + plane.d) / denom
                    intersect = p0 + t_param * d
                    self.log(
                        f"Intersection of {l_name} with {p_name}: ({intersect[0]:.2f}, {intersect[1]:.2f}, {intersect[2]:.2f})"
                    )

            else:
                raise ValueError("Select an operation")

        except Exception as exc:
            messagebox.showerror("Operation error", str(exc))

    # ---------------------------
    # Plotting
    # ---------------------------
    def update_plot(self):
        self.ax2d.cla()
        self.ax3d.cla()
        self.ax2d.grid(True)
        self.ax3d.grid(True)
        self.ax2d.set_xlim(-6, 6)
        self.ax2d.set_ylim(-6, 6)
        self.ax3d.set_xlim(-6, 6)
        self.ax3d.set_ylim(-6, 6)
        self.ax3d.set_zlim(-6, 6)
        self.ax2d.set_title("2D view")
        self.ax3d.set_title("3D view")

        for name, t, d, obj in self.objects:
            if t == "Vector":
                if d == "2D":
                    self.ax2d.arrow(0, 0, obj.x, obj.y, head_width=0.15, length_includes_head=True, color="C0")
                    self.ax2d.text(obj.x, obj.y, name)
                else:
                    self.ax3d.quiver(0, 0, 0, obj.x, obj.y, obj.z, color="C0")
                    self.ax3d.text(obj.x, obj.y, obj.z, name)
            elif t == "Point":
                if d == "2D":
                    self.ax2d.plot(obj.x, obj.y, "o", color="C1")
                    self.ax2d.text(obj.x, obj.y, name)
                else:
                    self.ax3d.scatter(obj.x, obj.y, obj.z, color="C1")
                    self.ax3d.text(obj.x, obj.y, obj.z, name)
            elif t == "Line":
                if d == "2D":
                    lam = np.linspace(-5, 5, 50)
                    pts = np.array([obj.point.to_array() + l * obj.direction.to_array() for l in lam])
                    self.ax2d.plot(pts[:, 0], pts[:, 1], label=name)
                    self.ax2d.plot(obj.point.x, obj.point.y, "o", color="C2")
                else:
                    lam = np.linspace(-5, 5, 50)
                    pts = np.array([obj.point.to_array() + l * obj.direction.to_array() for l in lam])
                    self.ax3d.plot(pts[:, 0], pts[:, 1], pts[:, 2], label=name)
                    self.ax3d.scatter(obj.point.x, obj.point.y, obj.point.z, color="C2")
            elif t == "Plane":
                p0 = obj.point_on_plane().to_array()
                n = obj.normal().to_array()
                if abs(n[2]) > 1e-9:
                    v1 = np.array([1, 0, -n[0] / n[2]])
                    v2 = np.array([0, 1, -n[1] / n[2]])
                else:
                    v1 = np.array([1, 0, 0])
                    v2 = np.array([0, 1, 0])
                s = np.linspace(-3, 3, 5)
                t_vals = np.linspace(-3, 3, 5)
                S, T = np.meshgrid(s, t_vals)
                X = p0[0] + S * v1[0] + T * v2[0]
                Y = p0[1] + S * v1[1] + T * v2[1]
                Z = p0[2] + S * v1[2] + T * v2[2]
                self.ax3d.plot_surface(X, Y, Z, alpha=0.3, color="C3")
                self.ax3d.quiver(p0[0], p0[1], p0[2], n[0], n[1], n[2], color="k")
                self.ax3d.text(p0[0], p0[1], p0[2], name)

        self.ax2d.legend(loc="upper right", fontsize="small")
        self.ax3d.legend(loc="upper right", fontsize="small")
        self.canvas.draw()


def main():
    root = tk.Tk()
    app = VisualiserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
