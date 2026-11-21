#!/usr/bin/env python3
"""FULLBODY2D: code-authored, shaded 2D anime scene prototype.

The output is a real 2D SVG composition rasterized frame-by-frame. The character
is a fully coloured human figure with anatomy, face, costume, shading and props.
There is no 3D stage or 3D model scene. Volume is created with 2D form drawing,
overlaps, cel shadows, highlights, perspective and surface detail.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cairosvg

WIDTH, HEIGHT, FPS, SECONDS = 1280, 720, 30, 6
FRAMES = FPS * SECONDS


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def smooth(a: float, b: float, x: float) -> float:
    u = clamp((x - a) / (b - a))
    return u * u * (3.0 - 2.0 * u)


def fmt(v: float) -> str:
    return f"{v:.3f}"


def definitions() -> str:
    return r"""
    <defs>
      <linearGradient id="night" x1="0" y1="0" x2="0.12" y2="1">
        <stop offset="0" stop-color="#090d20"/>
        <stop offset=".52" stop-color="#1c2140"/>
        <stop offset="1" stop-color="#090e1a"/>
      </linearGradient>
      <linearGradient id="skin" x1="0" y1="0" x2="1" y2=".22">
        <stop offset="0" stop-color="#f6c39d"/>
        <stop offset=".34" stop-color="#d99172"/>
        <stop offset=".68" stop-color="#a95852"/>
        <stop offset="1" stop-color="#623846"/>
      </linearGradient>
      <linearGradient id="skinLight" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#ffe1bd"/>
        <stop offset=".55" stop-color="#e9a17e"/>
        <stop offset="1" stop-color="#b96661"/>
      </linearGradient>
      <linearGradient id="hair" x1="0" y1="0" x2=".88" y2=".78">
        <stop offset="0" stop-color="#24385a"/>
        <stop offset=".25" stop-color="#121c34"/>
        <stop offset=".62" stop-color="#080d1d"/>
        <stop offset="1" stop-color="#030612"/>
      </linearGradient>
      <linearGradient id="hairLit" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#75e8ee"/>
        <stop offset=".35" stop-color="#345a84"/>
        <stop offset="1" stop-color="#11152b"/>
      </linearGradient>
      <linearGradient id="jacket" x1="0" y1="0" x2="1" y2=".3">
        <stop offset="0" stop-color="#2e4362"/>
        <stop offset=".28" stop-color="#16263e"/>
        <stop offset=".63" stop-color="#0c1529"/>
        <stop offset="1" stop-color="#070b19"/>
      </linearGradient>
      <linearGradient id="jacketLight" x1="0" y1="0" x2=".9" y2="1">
        <stop offset="0" stop-color="#6486a3"/>
        <stop offset=".25" stop-color="#294363"/>
        <stop offset=".8" stop-color="#111b31"/>
        <stop offset="1" stop-color="#081020"/>
      </linearGradient>
      <linearGradient id="trousers" x1="0" y1="0" x2="1" y2=".18">
        <stop offset="0" stop-color="#36405b"/>
        <stop offset=".32" stop-color="#202a43"/>
        <stop offset=".72" stop-color="#11182c"/>
        <stop offset="1" stop-color="#080e1e"/>
      </linearGradient>
      <linearGradient id="leather" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#617b91"/>
        <stop offset=".18" stop-color="#293c54"/>
        <stop offset=".6" stop-color="#101c30"/>
        <stop offset="1" stop-color="#050a17"/>
      </linearGradient>
      <linearGradient id="metal" x1="0" y1="0" x2="1" y2=".15">
        <stop offset="0" stop-color="#b4d5df"/>
        <stop offset=".18" stop-color="#40627b"/>
        <stop offset=".42" stop-color="#e0f6ef"/>
        <stop offset=".6" stop-color="#557d98"/>
        <stop offset="1" stop-color="#15243a"/>
      </linearGradient>
      <linearGradient id="blade" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#294a69"/>
        <stop offset=".32" stop-color="#d9f7f3"/>
        <stop offset=".48" stop-color="#ffffff"/>
        <stop offset=".62" stop-color="#69d9ed"/>
        <stop offset="1" stop-color="#203951"/>
      </linearGradient>
      <radialGradient id="neonCyan">
        <stop offset="0" stop-color="#baffff"/>
        <stop offset=".26" stop-color="#39dff1"/>
        <stop offset="1" stop-color="#0c637e" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="neonPink">
        <stop offset="0" stop-color="#ffe2e8"/>
        <stop offset=".28" stop-color="#ff5a9b"/>
        <stop offset="1" stop-color="#8b1d65" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#151c31"/>
        <stop offset=".58" stop-color="#0d1426"/>
        <stop offset="1" stop-color="#030713"/>
      </linearGradient>
      <filter id="softGlow" x="-80%" y="-80%" width="260%" height="260%">
        <feGaussianBlur stdDeviation="12"/>
      </filter>
      <filter id="shadow" x="-35%" y="-25%" width="170%" height="170%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="5" result="blur"/>
        <feOffset dy="6" dx="2" result="offset"/>
        <feComponentTransfer><feFuncA type="linear" slope=".42"/></feComponentTransfer>
        <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <pattern id="microHatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)">
        <path d="M0 0V8" stroke="#d4f4f7" stroke-width="1" opacity=".18"/>
      </pattern>
    </defs>
    """


def background(t: float) -> str:
    drift = 7.0 * math.sin(t * 0.45)
    windows = []
    for row in range(7):
        for col in range(10):
            x = 26 + col * 126 + (row % 2) * 29
            y = 80 + row * 54
            lit = (row * 7 + col * 11) % 6 in (0, 2)
            color = "#3fe3f0" if (row + col) % 3 else "#ff5598"
            windows.append(
                f'<rect x="{x}" y="{y}" width="28" height="18" rx="2" '
                f'fill="{color if lit else "#17223a"}" opacity="{0.6 if lit else 0.42}"/>'
            )
    rain = []
    for i in range(64):
        x = (i * 97.0 + t * (85 + (i % 5) * 18)) % 1360 - 30
        y = (i * 53.0 + t * (180 + (i % 7) * 16)) % 760
        rain.append(f'<path d="M{fmt(x)} {fmt(y)} l-5 22" stroke="#8cd6e8" '
                    f'stroke-width="{1 if i % 5 else 1.7}" opacity=".28"/>')
    building_lines = []
    for i in range(13):
        x = -40 + i * 110
        building_lines.append(f'<path d="M{x} 0 V{220+(i%4)*45} l-18 30" fill="none" '
                             f'stroke="#31425f" stroke-width="5" opacity=".65"/>')
    return f"""
    <rect width="1280" height="720" fill="url(#night)"/>
    <circle cx="1040" cy="180" r="180" fill="url(#neonCyan)" opacity=".17"/>
    <circle cx="230" cy="250" r="210" fill="url(#neonPink)" opacity=".12"/>
    <g transform="translate({fmt(drift)} 0)">
      <path d="M0 0 H1280 V402 H0Z" fill="#11182c"/>
      <path d="M0 0 H1280 V160 L1080 190 930 145 760 196 590 145 390 204 190 153 0 220Z"
            fill="#090f20"/>
      <path d="M0 250 L105 175 244 213 350 150 520 230 660 145 810 204 1005 139 1165 205 1280 166 V510 H0Z"
            fill="#151d34"/>
      {"".join(building_lines)}
      {"".join(windows)}
      <g opacity=".7" fill="none" stroke-linecap="round">
        <path d="M0 125 Q180 115 320 156 T650 143 T980 127 T1280 139" stroke="#324a6e" stroke-width="4"/>
        <path d="M-30 175 Q160 148 325 188 T670 169 T990 172 T1300 184" stroke="#172c47" stroke-width="8"/>
        <path d="M70 0 V345 M1185 0 V310" stroke="#253d5a" stroke-width="9"/>
      </g>
      <g transform="translate(90 292)">
        <rect x="0" y="0" width="200" height="112" rx="7" fill="#0a1224" stroke="#3b6b82" stroke-width="4"/>
        <rect x="12" y="12" width="176" height="88" rx="3" fill="#102d45"/>
        <path d="M25 25 H173 M25 42 H151 M25 59 H163 M25 76 H125" stroke="#51d6e5" stroke-width="3" opacity=".62"/>
        <circle cx="164" cy="82" r="8" fill="#ff5c9c"/>
      </g>
      <g transform="translate(1015 258)">
        <rect x="0" y="0" width="180" height="142" rx="8" fill="#10172b" stroke="#b53d75" stroke-width="4"/>
        <rect x="13" y="13" width="154" height="116" rx="4" fill="#1b2540"/>
        <path d="M30 34 H150 M30 54 H128 M30 74 H150 M30 94 H103" stroke="#f07aae" stroke-width="4" opacity=".75"/>
      </g>
    </g>
    <path d="M0 385 L1280 385 V720 H0Z" fill="url(#road)"/>
    <path d="M0 398 L610 408 1280 394" stroke="#426079" stroke-width="3" opacity=".7" fill="none"/>
    <path d="M0 720 L430 420 850 420 1280 720Z" fill="#0a1222" opacity=".5"/>
    <g stroke="#293d5a" stroke-width="2" opacity=".7" fill="none">
      <path d="M0 470 L1280 470 M0 542 L1280 542 M0 626 L1280 626"/>
      <path d="M640 407 L0 720 M640 407 L1280 720"/>
      <path d="M210 405 L0 720 M1060 405 L1280 720"/>
    </g>
    <g opacity=".62">
      <path d="M470 460 Q640 442 820 460" stroke="#36ddeb" stroke-width="7" fill="none" filter="url(#softGlow)"/>
      <path d="M870 510 Q1000 500 1160 520" stroke="#f04b90" stroke-width="9" fill="none" filter="url(#softGlow)"/>
      <path d="M0 590 Q180 563 342 586" stroke="#46d9e7" stroke-width="4" fill="none"/>
    </g>
    <g opacity=".8">
      <path d="M0 679 Q180 664 330 684 T690 684 T1020 673 T1280 681" stroke="#30475e" stroke-width="3" fill="none"/>
      <path d="M90 690 l170 -5 M980 698 l180 -8" stroke="#6b91a3" stroke-width="2" opacity=".5"/>
    </g>
    <g>{''.join(rain)}</g>
    <g transform="translate(1045 420) rotate(-8)">
      <ellipse cx="0" cy="0" rx="76" ry="22" fill="#091326" stroke="#4d7b91" stroke-width="3"/>
      <path d="M-63 -6 Q0 -44 63 -6 L43 9 Q0 29 -43 9Z" fill="#243e59" stroke="#92c9d7" stroke-width="3"/>
      <path d="M-26 -14 L-5 -36 25 -18" fill="none" stroke="#d1eff0" stroke-width="4"/>
      <ellipse cx="0" cy="-5" rx="15" ry="6" fill="#fa5b9d"/>
      <path d="M-72 1 L-93 11 M72 1 L93 11" stroke="#64dbe8" stroke-width="5"/>
      <circle cx="-86" cy="12" r="6" fill="#ff619d"/><circle cx="86" cy="12" r="6" fill="#51e9f4"/>
    </g>
    """


def character(t: float) -> str:
    # A coherent full-body illustrated person. Motion is a small 2D action cycle:
    # anticipation, weight shift, a brief blade sweep and recovery.
    phase = t * math.tau * 0.55
    bob = 4.2 * math.sin(phase)
    run = smooth(1.85, 2.55, t) * (1.0 - smooth(4.0, 4.85, t))
    impact = smooth(2.55, 3.0, t) * (1.0 - smooth(3.5, 4.15, t))
    root_x = 425 + 10 * math.sin(t * 0.5) + 16 * run
    leg_back = 7.0 * math.sin(phase + 2.5) + 7 * run
    leg_front = -6.0 * math.sin(phase + 2.5) - 11 * run
    arm_back = -4.0 + 7.0 * math.sin(phase + 1.2)
    arm_front = 3.0 + 7.0 * math.sin(phase + 3.2) - 17 * impact
    head_turn = 1.7 * math.sin(phase * .7)
    blade_angle = -8.0 - 22.0 * impact + 6.0 * run
    hair_wind = 8.0 * math.sin(t * 2.8) + 13 * run

    return f"""
    <g transform="translate({fmt(root_x)} {fmt(42+bob)}) scale(.96)" filter="url(#shadow)">
      <ellipse cx="205" cy="643" rx="161" ry="19" fill="#020713" opacity=".82"/>
      <!-- Coat tails, designed as full fabric forms with lit edges and fold planes. -->
      <g transform="rotate({fmt(4+5*math.sin(phase))} 215 290)">
        <path d="M122 252 C93 300 86 372 96 445 L56 560 Q92 540 119 512 L150 391Z"
              fill="url(#jacket)" stroke="#050b18" stroke-width="7" stroke-linejoin="round"/>
        <path d="M258 254 C303 300 326 375 322 451 L372 540 Q332 533 294 499 L255 390Z"
              fill="#101b30" stroke="#040a17" stroke-width="7" stroke-linejoin="round"/>
        <path d="M103 364 Q121 400 112 476 L82 523 M307 370 Q286 409 306 475 L348 514"
              fill="none" stroke="#719ab1" stroke-width="5" opacity=".72"/>
        <path d="M125 278 Q110 330 133 376 M274 278 Q305 332 286 382"
              fill="none" stroke="#080f22" stroke-width="10" opacity=".72"/>
      </g>

      <!-- Rear leg: complete trouser volume, articulated but not a wireframe. -->
      <g transform="rotate({fmt(leg_back)} 197 376)">
        <path d="M154 350 C122 368 119 405 130 449 L143 510
                 C143 526 137 557 130 587 Q154 602 184 592
                 L205 518 C213 486 205 455 211 431
                 C219 397 203 366 184 352Z"
              fill="url(#trousers)" stroke="#050b18" stroke-width="8" stroke-linejoin="round"/>
        <path d="M145 391 Q167 408 187 411 L176 452 Q159 462 150 447Z"
              fill="#101b30" stroke="#59758c" stroke-width="3"/>
        <path d="M135 454 Q157 469 199 465 L190 491 Q161 501 145 486Z"
              fill="#070e20" opacity=".85"/>
        <path d="M151 506 Q172 517 199 509 L188 552 Q169 561 143 548Z"
              fill="#293b55" opacity=".72"/>
        <path d="M160 389 Q149 423 161 447 M192 464 Q179 493 181 524"
              fill="none" stroke="#91b7c3" stroke-width="3" opacity=".56"/>
        <path d="M138 578 Q163 590 185 580 L192 620 Q165 638 121 624
                 L113 607 Q119 591 138 578Z"
              fill="url(#leather)" stroke="#030814" stroke-width="8" stroke-linejoin="round"/>
        <path d="M127 599 Q153 608 186 595 M123 617 Q154 626 190 610"
              fill="none" stroke="#8bb6c5" stroke-width="4" opacity=".62"/>
        <path d="M134 632 Q160 640 196 625 L205 644 Q174 665 116 653Z"
              fill="#030814" stroke="#080c18" stroke-width="5"/>
        <path d="M147 608 L158 617 L177 606" fill="none" stroke="#d6f3e9" stroke-width="3"/>
      </g>

      <!-- Front leg and boot. -->
      <g transform="rotate({fmt(leg_front)} 246 377)">
        <path d="M209 350 C236 337 278 356 287 391
                 C294 419 283 453 276 480 L272 530
                 C269 552 283 582 290 603
                 Q257 620 220 603 L203 555
                 C191 528 190 497 195 470
                 C201 438 189 407 195 381Z"
              fill="url(#trousers)" stroke="#050b18" stroke-width="8" stroke-linejoin="round"/>
        <path d="M211 389 Q240 403 278 393 L267 422 Q238 439 207 423Z"
              fill="#101a2e" stroke="#647f95" stroke-width="3"/>
        <path d="M202 458 Q235 470 282 447 L273 481 Q239 501 202 485Z"
              fill="#090f20" opacity=".9"/>
        <path d="M203 512 Q231 526 270 509 L280 550 Q253 570 218 554Z"
              fill="#30415a" opacity=".68"/>
        <path d="M218 400 Q231 431 222 454 M267 465 Q248 493 244 519"
              stroke="#a0c0c9" stroke-width="3" opacity=".48" fill="none"/>
        <path d="M221 578 Q255 591 291 573 L313 618
                 Q283 647 221 632 L201 606Z"
              fill="url(#leather)" stroke="#030814" stroke-width="8" stroke-linejoin="round"/>
        <path d="M224 590 Q260 607 299 587 M214 610 Q258 627 306 606"
              stroke="#91b7c6" stroke-width="4" opacity=".72" fill="none"/>
        <path d="M218 633 Q261 650 311 623 L327 646
                 Q286 672 208 659Z"
              fill="#030814" stroke="#080d18" stroke-width="5"/>
        <path d="M248 604 L261 616 L282 602" stroke="#d8f7ef" stroke-width="3" fill="none"/>
        <rect x="220" y="580" width="75" height="12" rx="5" fill="#0a1223" stroke="#5e8298" stroke-width="3"/>
      </g>

      <!-- Belt, hip armour and hanging equipment. -->
      <path d="M118 337 Q207 359 294 331 L303 366 Q208 390 112 367Z"
            fill="#101a2c" stroke="#030814" stroke-width="7"/>
      <path d="M193 351 L225 352 L230 377 L190 377Z" fill="url(#metal)" stroke="#030814" stroke-width="4"/>
      <rect x="135" y="355" width="39" height="49" rx="5" fill="#14253b" stroke="#6a8a9b" stroke-width="4"/>
      <path d="M144 365 H164 M144 375 H164 M144 385 H158" stroke="#9ec5ce" stroke-width="3"/>
      <path d="M284 358 L320 367 L313 427 Q293 420 279 397Z"
            fill="#182840" stroke="#050b18" stroke-width="6"/>
      <path d="M294 371 L306 379 L301 405" fill="none" stroke="#8aaab8" stroke-width="3"/>

      <!-- Torso and complete layered costume. -->
      <path d="M135 170 C106 179 82 202 78 245
               C74 288 86 327 104 365
               Q190 390 291 359
               C308 319 312 256 291 210
               C276 181 249 171 218 165
               L190 185 L161 165Z"
            fill="url(#jacket)" stroke="#040a17" stroke-width="9" stroke-linejoin="round"/>
      <path d="M160 177 Q189 204 216 177 L247 205
               Q232 257 250 334 L202 359 L139 338
               Q155 271 126 207Z"
            fill="#101e35" stroke="#6f8ea0" stroke-width="4"/>
      <path d="M166 190 L194 215 L220 188 L243 211
               L222 257 L198 282 L173 253 L147 211Z"
            fill="url(#jacketLight)" stroke="#070d1c" stroke-width="5"/>
      <path d="M192 216 L207 226 L222 214 L236 250
               L215 282 L196 300 L180 270Z"
            fill="#101a2d" stroke="#050b17" stroke-width="4"/>
      <path d="M137 205 Q112 251 129 296 L111 322
               Q91 274 104 223Z"
            fill="#314c68" stroke="#081020" stroke-width="4"/>
      <path d="M274 209 Q295 252 279 310 L296 336
               Q315 264 290 218Z"
            fill="#0a1427" stroke="#050a16" stroke-width="4"/>
      <path d="M147 219 Q160 257 150 300 M245 223 Q256 267 247 310"
            fill="none" stroke="#a3c3c9" stroke-width="4" opacity=".6"/>
      <path d="M171 284 Q191 300 215 281 M165 310 Q193 324 225 305"
            fill="none" stroke="#080f21" stroke-width="8" opacity=".8"/>
      <path d="M125 331 Q190 350 271 329" fill="none" stroke="#83a6b8" stroke-width="4"/>
      <path d="M132 242 L151 258 L148 277 L130 264 M266 247 L247 270 L250 288"
            fill="none" stroke="#e2b28e" stroke-width="2.6" opacity=".62"/>
      <path d="M184 231 L193 251 L202 234" fill="none" stroke="#d9f7e9" stroke-width="4"/>
      <path d="M205 258 L220 274 L207 291" fill="none" stroke="#5ce3ef" stroke-width="4" opacity=".8"/>
      <path d="M112 294 L137 315 M271 292 L247 317" stroke="#d1f5f0" stroke-width="3" opacity=".45"/>

      <!-- Shirt, collar, neck and neck tendons. -->
      <path d="M174 147 Q203 164 232 146 L240 199
               Q216 223 194 224 Q170 210 158 191Z"
            fill="url(#skin)" stroke="#080e1b" stroke-width="6"/>
      <path d="M183 172 Q202 189 221 173 L231 194
               Q209 212 189 198Z" fill="#713f4b" opacity=".7"/>
      <path d="M172 168 L191 193 L181 222 L149 196Z"
            fill="#d7e9e4" stroke="#07101d" stroke-width="5"/>
      <path d="M224 169 L206 195 L218 220 L250 190Z"
            fill="#b9d0d1" stroke="#07101d" stroke-width="5"/>
      <path d="M188 178 Q184 197 194 207 M218 180 Q225 196 214 208"
            stroke="#f4c29d" stroke-width="4" fill="none"/>

      <!-- Rear arm: entire sleeve, elbow volume and cuff. -->
      <g transform="rotate({fmt(arm_back)} 101 206)">
        <path d="M113 197 C91 185 65 195 54 218
                 C43 241 48 271 62 292 L82 326
                 Q102 338 123 320 L109 286
                 Q103 262 119 235Z"
              fill="url(#jacketLight)" stroke="#040a18" stroke-width="8"/>
        <path d="M62 225 Q88 224 105 244 L91 276
                 Q73 271 57 252Z" fill="#13233b"/>
        <path d="M63 259 Q87 271 104 263 L113 291
                 Q91 306 73 290Z" fill="#0b1428"/>
        <path d="M70 220 Q88 211 100 225 M78 284 Q91 296 103 287"
              fill="none" stroke="#9dbbc3" stroke-width="4" opacity=".58"/>
        <path d="M75 312 Q98 326 120 312 L131 335
                 Q109 352 82 338Z"
              fill="#152840" stroke="#030915" stroke-width="6"/>
        <path d="M82 322 L118 333 M86 335 L114 344" stroke="#7da2b2" stroke-width="3"/>
      </g>

      <!-- Front arm and hand on the sword grip. -->
      <g transform="rotate({fmt(arm_front)} 280 202)">
        <path d="M269 190 C296 184 321 202 326 229
                 C330 249 316 271 309 290
                 L292 328 Q270 342 250 322
                 L264 281 Q271 261 261 238Z"
              fill="url(#jacketLight)" stroke="#030a18" stroke-width="8"/>
        <path d="M284 207 Q310 212 313 238 L294 262
                 Q275 255 270 235Z" fill="#2e4c69"/>
        <path d="M271 262 Q292 274 316 264 L304 295
                 Q281 306 258 288Z" fill="#0a1427"/>
        <path d="M278 214 Q294 231 288 252 M277 278 Q297 289 307 281"
              fill="none" stroke="#c4dce0" stroke-width="4" opacity=".58"/>
        <path d="M268 309 Q288 322 307 310 L318 334
                 Q292 349 263 333Z" fill="#111d31" stroke="#040a17" stroke-width="6"/>
        <path d="M275 317 L309 331" stroke="#76a2b4" stroke-width="4"/>
        <!-- Gloved palm and individually readable fingers. -->
        <path d="M282 331 Q298 316 316 330
                 Q329 340 321 355 L303 371
                 Q286 373 275 358Z"
              fill="url(#leather)" stroke="#030815" stroke-width="6"/>
        <path d="M282 340 Q272 347 266 361 Q266 370 276 371
                 Q287 366 292 352"
              fill="#172a40" stroke="#030815" stroke-width="5"/>
        <path d="M301 347 Q315 350 321 364 Q320 374 310 374
                 Q299 366 298 355
                 M290 357 Q299 364 296 380 Q291 388 283 381
                 Q278 369 284 359"
              fill="#263c55" stroke="#030815" stroke-width="4"/>
        <path d="M278 350 L290 356 M289 367 L299 372" stroke="#a2c7ce" stroke-width="2.5"/>
      </g>

      <!-- Sword: 2D designed metallic asset with bevels, guard and wrapped grip. -->
      <g transform="translate(0 0) rotate({fmt(blade_angle)} 315 335)">
        <path d="M317 334 Q328 231 353 91 Q359 53 370 34
                 Q372 116 359 202 L333 343Z"
              fill="url(#blade)" stroke="#07101e" stroke-width="6" stroke-linejoin="round"/>
        <path d="M330 320 Q342 208 363 76" stroke="#f3ffff" stroke-width="5" fill="none" opacity=".88"/>
        <path d="M336 330 Q351 216 369 110" stroke="#4fd7e9" stroke-width="3" fill="none"/>
        <path d="M300 339 Q327 327 351 344 L346 358 Q323 349 298 362Z"
              fill="url(#metal)" stroke="#050b18" stroke-width="6"/>
        <path d="M319 352 L304 416 Q319 431 334 418 L330 356Z"
              fill="#101c31" stroke="#050b18" stroke-width="6"/>
        <path d="M307 365 L329 383 M304 381 L326 399 M301 398 L323 414"
              stroke="#94bfca" stroke-width="4"/>
        <circle cx="325" cy="347" r="7" fill="#f5d8a7" stroke="#101a2c" stroke-width="3"/>
      </g>

      <!-- Complete face and head, turned slightly in three-quarter view. -->
      <g transform="rotate({fmt(head_turn)} 205 110)">
        <path d="M145 66 C155 38 190 25 222 39
                 C253 51 264 87 254 125
                 C249 151 231 177 208 184
                 C180 184 157 163 148 139
                 C139 112 133 90 145 66Z"
              fill="url(#skin)" stroke="#050c19" stroke-width="7" stroke-linejoin="round"/>
        <path d="M222 47 Q260 68 249 120 Q241 156 212 174
                 Q228 137 220 112 Q235 86 222 47Z"
              fill="#713d4a" opacity=".68"/>
        <path d="M147 92 Q155 64 174 60 Q166 89 177 116
                 Q164 147 180 168 Q151 152 143 121Z"
              fill="#f7c49f" opacity=".5"/>
        <path d="M157 110 Q174 94 192 108 Q183 122 160 122Z"
              fill="#f4dfcb" stroke="#351e31" stroke-width="3"/>
        <path d="M206 106 Q225 94 242 105 Q230 118 207 119Z"
              fill="#f2dfce" stroke="#351e31" stroke-width="3"/>
        <ellipse cx="178" cy="111" rx="7" ry="10" fill="#37b9d0"/>
        <ellipse cx="225" cy="108" rx="7" ry="9" fill="#279ebc"/>
        <ellipse cx="180" cy="112" rx="3.3" ry="6.7" fill="#081226"/>
        <ellipse cx="227" cy="109" rx="3.3" ry="6.2" fill="#081226"/>
        <circle cx="182" cy="108" r="2.4" fill="#fff"/>
        <circle cx="229" cy="105" r="2.2" fill="#fff"/>
        <path d="M154 98 Q174 82 193 98 M204 95 Q224 80 243 95"
              fill="none" stroke="#101426" stroke-width="8" stroke-linecap="round"/>
        <path d="M198 112 Q195 128 189 140 Q201 147 212 141"
              fill="none" stroke="#914f53" stroke-width="5" stroke-linecap="round"/>
        <path d="M189 155 Q205 161 220 151 Q216 168 201 169 Q191 167 189 155Z"
              fill="#8a3d4a" stroke="#562c3e" stroke-width="3"/>
        <path d="M193 157 Q204 161 216 155" stroke="#ffd0b5" stroke-width="3" fill="none"/>
        <path d="M160 134 Q171 145 180 143 M226 132 Q236 135 241 126"
              fill="none" stroke="#9a5454" stroke-width="3" opacity=".65"/>
        <path d="M151 77 Q164 45 201 43 Q233 43 251 71
                 Q243 54 218 49 Q193 32 165 59Z"
              fill="#f5b18f" opacity=".48"/>
        <path d="M149 135 Q157 158 177 173" stroke="#f5c29e" stroke-width="4" fill="none" opacity=".75"/>
        <!-- Ear with internal structure. -->
        <path d="M145 111 Q125 97 121 121 Q123 147 147 149Z"
              fill="url(#skinLight)" stroke="#512e3d" stroke-width="5"/>
        <path d="M128 119 Q140 112 139 131 Q133 141 130 132"
              fill="none" stroke="#98505a" stroke-width="4"/>
        <!-- Hair: layered locks, not a single helmet shape. -->
        <g transform="translate(0 0) rotate({fmt(hair_wind)} 203 74)">
          <path d="M135 101 Q117 71 137 43 Q128 10 166 18
                   Q187 -7 215 19 Q246 9 262 39
                   Q282 55 263 91 L249 84 L245 59
                   Q229 75 215 82 L209 51
                   Q192 79 171 88 L166 57
                   Q151 90 135 101Z"
                fill="url(#hair)" stroke="#030714" stroke-width="8" stroke-linejoin="round"/>
          <path d="M139 61 Q151 25 176 27 Q160 48 165 71
                   Q149 79 139 92Z"
                fill="url(#hairLit)" stroke="#091427" stroke-width="3"/>
          <path d="M172 26 Q194 2 215 28 Q197 39 189 68
                   Q177 65 172 26Z"
                fill="#172c4d" stroke="#030714" stroke-width="4"/>
          <path d="M216 25 Q249 21 258 54 Q241 46 232 78
                   Q218 62 216 25Z"
                fill="#0c1830" stroke="#030714" stroke-width="4"/>
          <path d="M145 55 Q163 32 176 34 M183 28 Q198 16 210 30
                   M225 34 Q242 32 250 48"
                fill="none" stroke="#8ae6ed" stroke-width="4" opacity=".72"/>
          <path d="M141 88 Q151 75 163 62 M184 59 Q199 43 208 40
                   M226 67 Q240 55 252 60"
                stroke="#52789a" stroke-width="3.5" fill="none"/>
          <path d="M135 85 Q117 113 129 138 Q139 121 149 109
                   M245 82 Q263 101 255 123 L238 108"
                fill="#111e38" stroke="#030714" stroke-width="6"/>
        </g>
      </g>

      <!-- Costume construction details: zips, seam paths, folds, straps and metal hardware. -->
      <g fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M130 225 Q118 267 130 314 M280 224 Q293 270 279 312"
              stroke="#80a9b9" stroke-width="4" opacity=".72"/>
        <path d="M154 218 Q170 245 164 270 M239 218 Q226 248 234 272"
              stroke="#030a18" stroke-width="5"/>
        <path d="M165 276 L182 293 L174 315 M240 284 L224 305 L236 319"
              stroke="#8baab8" stroke-width="3" opacity=".65"/>
        <path d="M120 300 L145 315 M263 302 L243 320" stroke="#e8ba97" stroke-width="3"/>
        <path d="M198 233 L203 337" stroke="#9bbbc4" stroke-width="3"/>
        <path d="M189 254 L200 258 L210 253 M189 270 L200 274 L210 269"
              stroke="#c5e3e3" stroke-width="3"/>
        <path d="M148 351 Q175 363 191 360 M233 363 Q264 359 284 348"
              stroke="#87a8b7" stroke-width="3"/>
        <path d="M142 373 L140 403 M289 375 L286 404" stroke="#4c718c" stroke-width="4"/>
      </g>
      <g>
        <circle cx="133" cy="293" r="5" fill="#f5cb9c" stroke="#071020" stroke-width="3"/>
        <circle cx="278" cy="292" r="5" fill="#f5cb9c" stroke="#071020" stroke-width="3"/>
        <rect x="149" y="245" width="8" height="32" rx="3" fill="#a7d2d7" opacity=".75"/>
        <rect x="255" y="242" width="8" height="31" rx="3" fill="#a7d2d7" opacity=".7"/>
      </g>
      <!-- Hairline rim and rain highlights make the figure sit inside the 2D lighting design. -->
      <path d="M150 57 Q174 17 208 21" stroke="#6de6ed" stroke-width="3" opacity=".7" fill="none"/>
      <path d="M86 212 Q70 243 78 267 M291 210 Q309 242 299 271"
            stroke="#5cdded" stroke-width="4" fill="none" opacity=".58"/>
      <path d="M205 387 Q220 399 246 392" stroke="#ff6b9d" stroke-width="4" fill="none" opacity=".65"/>
      <path d="M151 526 Q169 533 187 526 M235 540 Q252 546 272 534"
            stroke="#5ce3ed" stroke-width="3" fill="none" opacity=".52"/>
      <!-- Brief energy glint on the sword during the strike beat. -->
      <g opacity="{fmt(0.25+0.75*impact)}">
        <path d="M338 167 L370 119 M332 183 L374 135 M344 190 L385 149"
              stroke="#c7ffff" stroke-width="4" fill="none" filter="url(#softGlow)"/>
      </g>
    </g>
    """


def effects(t: float) -> str:
    impact = smooth(2.55, 3.0, t) * (1.0 - smooth(3.5, 4.15, t))
    arcs = []
    if impact > .02:
        for i in range(13):
            x = 790 + i * 18
            y = 220 + math.sin(i * .7 + t * 4) * 50
            arcs.append(
                f'<path d="M{fmt(x)} {fmt(y)} l{fmt(18+impact*15)} {fmt(-30-impact*35)}" '
                f'stroke="#a9f7ff" stroke-width="{fmt(1.5+impact*2)}" opacity="{fmt(.25+impact*.55)}" fill="none"/>'
            )
    return f"""
    <g>{''.join(arcs)}</g>
    <g opacity="{fmt(.3+impact*.5)}">
      <circle cx="792" cy="288" r="{fmt(14+impact*34)}" fill="none" stroke="#51e6f0" stroke-width="3"/>
      <circle cx="792" cy="288" r="{fmt(28+impact*52)}" fill="none" stroke="#f45e9d" stroke-width="2" opacity=".72"/>
    </g>
    """


def frame_svg(frame: int) -> str:
    t = (frame - 1) / FPS
    camera_x = -4.0 * math.sin(t * .42)
    camera_y = 2.0 * math.sin(t * .6)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
    {definitions()}
    <g transform="translate({fmt(camera_x)} {fmt(camera_y)})">
      {background(t)}
      {character(t)}
      {effects(t)}
    </g>
    <rect width="1280" height="720" fill="url(#microHatch)" opacity=".14"/>
    <path d="M22 22 H1258 V698 H22Z" stroke="#77d7df" stroke-width="2" opacity=".22" fill="none"/>
    </svg>"""


def render(output_dir: Path) -> dict:
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for frame in range(1, FRAMES + 1):
        svg = frame_svg(frame)
        png_path = frames_dir / f"frame_{frame:04d}.png"
        cairosvg.svg2png(
            bytestring=svg.encode("utf-8"),
            write_to=str(png_path),
            output_width=WIDTH,
            output_height=HEIGHT,
        )
        if frame == 1:
            (output_dir / "fullbody2d-scene.svg").write_text(svg, encoding="utf-8")
    manifest = {
        "pipeline": "FULLBODY2D",
        "stage": "2D canvas only",
        "renderer": "Python-authored SVG scene + CairoSVG rasterization",
        "fps": FPS,
        "seconds": SECONDS,
        "frames": FRAMES,
        "resolution": [WIDTH, HEIGHT],
        "audio": "none",
        "reference_video_frames_in_final_output": False,
        "character": {
            "design": "original adult anime-style human, complete full-body illustration",
            "rendering": "full colour, form gradients, cel-shadow planes, highlights, material details and ink contours",
            "anatomy_parts": [
                "skull and jaw", "ears", "eyes and eyelids", "irises and pupils",
                "eyebrows", "nose", "mouth", "neck", "shoulders", "ribcage",
                "pelvis", "upper arms", "forearms", "wrists", "hands", "fingers",
                "thighs", "knees", "calves", "ankles", "feet", "boots"
            ],
            "costume_parts": [
                "layered jacket", "collar", "shirt", "lapels", "seams", "fold planes",
                "belt", "pouch", "cuffs", "straps", "boots", "metal fasteners"
            ],
            "hair": "multiple designed locks, clumps, flyaways, highlight planes",
            "props": ["designed metallic sword with bevel highlights and wrapped grip"],
            "motion": ["weight shift", "breathing bob", "leg swing", "arm movement",
                       "blade sweep", "hair and coat follow-through", "2D camera drift"]
        },
        "forbidden_shortcuts": [
            "stick figures", "wireframe people", "unshaded outline-only characters",
            "flat icon people", "3D environment scene", "reference footage in final"
        ]
    }
    (output_dir / "fullbody2d-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    render(out)
    print(f"Rendered {FRAMES} full-colour 2D frames to {out}")


if __name__ == "__main__":
    main()
