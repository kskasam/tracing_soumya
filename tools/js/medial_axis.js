// medial_axis.js

// Load libraries from CDN
import MA from "https://cdn.jsdelivr.net/npm/@flatten-js/medial-axis/+esm";
import { pathToPolys } from "https://cdn.jsdelivr.net/npm/svg-path-to-polygons/+esm";

// Convert SVG path → polygon → medial axis skeleton
export async function computeCenterline(svgPathString) {
    try {
        let polygons = pathToPolys(svgPathString, {
            tolerance: 1,
            decimals: 1,
        });

        let mainPolygon = polygons[0];
        let skeleton = MA(mainPolygon);

        // Convert skeleton edges → SVG path
        let d = "";
        skeleton.edges.forEach(edge => {
            d += `M ${edge.start.x} ${edge.start.y} L ${edge.end.x} ${edge.end.y} `;
        });

        return d.trim();

    } catch (err) {
        console.error("Medial Axis Error:", err);
        return "";
    }
}
