# tests/test_road_ribbon_spec.py
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "universal-city-compiler"))
from road_ribbon_spec import sample_planview

XODR_LINE = """<OpenDRIVE><road name="r" length="10.0" id="1" junction="-1">
<planView><geometry s="0" x="0" y="0" hdg="0" length="10.0"><line/></geometry>
</planView></road></OpenDRIVE>"""

XODR_ARC = """<OpenDRIVE><road name="r" length="31.4159" id="1" junction="-1">
<planView><geometry s="0" x="0" y="0" hdg="0" length="31.4159"><arc curvature="0.031831"/></geometry>
</planView></road></OpenDRIVE>"""


def test_line_samples_endpoints():
    pts = sample_planview(ET.fromstring(XODR_LINE).find("road"), step_m=2.0)
    assert pts[0] == (0.0, 0.0)
    assert abs(pts[-1][0] - 10.0) < 1e-6 and abs(pts[-1][1]) < 1e-6
    assert len(pts) == 6  # 0,2,4,6,8,10


def test_arc_endpoints_match_geometry_math():
    # k=0.031831, L=31.4159 -> dtheta ~= 1.0 rad
    pts = sample_planview(ET.fromstring(XODR_ARC).find("road"), step_m=2.0)
    k, L = 0.031831, 31.4159
    ex = (1.0 / k) * math.sin(k * L)   # hdg0 = 0
    ey = (1.0 / k) * (1.0 - math.cos(k * L))
    assert abs(pts[-1][0] - ex) < 0.05 and abs(pts[-1][1] - ey) < 0.05


def test_no_duplicate_joint_points():
    xodr = """<OpenDRIVE><road name="r" length="20.0" id="1" junction="-1">
    <planView>
      <geometry s="0" x="0" y="0" hdg="0" length="10.0"><line/></geometry>
      <geometry s="10.0" x="10.0" y="0" hdg="0" length="10.0"><line/></geometry>
    </planView></road></OpenDRIVE>"""
    pts = sample_planview(ET.fromstring(xodr).find("road"), step_m=2.0)
    assert len(pts) == len(set(pts))
