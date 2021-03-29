import React from 'react';
import './Mymap.css';
import L from 'leaflet';
import { INITIAL_ZOOM }  from '../../../configurations'

let configs = require('configurations');

class Mymap extends React.Component {

    constructor (props) {
        super(props);
        this.state={
            zoom:INITIAL_ZOOM,
            center:'world',
            myMap: null,
            graph_summary: null
        }
    }

    render() {
        return <div className={'border flex-1'}>
            <div>Zoom level: {this.state.zoom}</div>
            <div id="mapid"/>

        </div>;
    }

    componentDidMount() {

        // TODO: this call is repeated in map header, create container component and move up in the hierarchy so it's shared
        fetch(configs['endpoints']['base'] + configs['endpoints']['graph_summary'])
            .then(response =>
                response.json())
            .then(data => {
                console.log(data)
                this.setState({"graph_summary": data})
            })
        // TODO: do it properly
        setTimeout(() => {  console.log("World!"); }, 2000);

        let corner1 = L.latLng(0, 0);
        let corner2 = L.latLng(- configs['tile_size'], configs['tile_size']);
        let bounds = L.latLngBounds(corner1, corner2); // stops panning (scrolling around)  maxBounds: bounds

        const myMap = L.map('mapid' , {
            noWrap: true,
            crs: L.CRS.Simple,
            maxBounds: bounds,
            maxBoundsViscosity: 0.9
        }).setView([configs['tile_size'] / -2, configs['tile_size'] / 2], INITIAL_ZOOM);

        this.setState({myMap: myMap})

        const layer = L.tileLayer(configs['endpoints']['base'] + configs['endpoints']['tile'] + '/{z}/{x}/{y}.png', {
            maxZoom: configs['zoom_levels'] - 1,
            attribution: 'tokengallery 2.0',
            tileSize: configs['tile_size']
        }).addTo(myMap);

        let popup = L.popup()
            .setContent('<p>Hello world!<br />This is a nice popup.</p>')

        fetch(configs['endpoints']['base'] + configs['endpoints']['interest_points'])
            .then(response =>
                response.json())
            .then(data => {
                for (let p in data) {
                    let pos = convert_graph_coordinate_to_map(parseTuple(p),
                        this.state.graph_summary['min_coordinate'], this.state.graph_summary['max_coordinate']);

                    let myIcon = L.divIcon({className: 'my-div-icon'});
                    L.marker(pos, {icon: myIcon})
                        .bindPopup(popup).openPopup()
                        .addTo(myMap);
                }

                let pos = convert_graph_coordinate_to_map(parseTuple("(-209.191757, 78.224487)"),
                    this.state.graph_summary['min_coordinate'], this.state.graph_summary['max_coordinate']);

                let myIcon = L.divIcon({className: 'my-div-icon'});
                L.marker(pos, {icon: myIcon})
                    .bindPopup(popup).openPopup()
                    .addTo(myMap);

            });

        myMap.on('zoom', function () {
            // console.log("on zoom callback")
            this.setState({zoom: myMap.getZoom()})
        }.bind(this))
    }
}

Mymap.propTypes = {};

Mymap.defaultProps = {};

export default Mymap;

// TODO: move somewhere else

/**
 * Given a graph coordinate (as generated by force atlas 2) it returns the
 * corresponding coordinate on the map.
 *
 * @param graph_coordinate
 * @param g_min: this should be the smallest number appearing either as x or y among all
 * the coordinates of the graph
 * @param g_max same as g_min but the largest number
 */
function convert_graph_coordinate_to_map(graph_coordinate, g_min, g_max){
    let graph_side = g_max - g_min
    let map_x = (graph_coordinate[0] + Math.abs(g_min)) * configs["tile_size"] / graph_side
    let map_y = (graph_coordinate[1] + Math.abs(g_min)) * configs["tile_size"] / graph_side
    return [- map_y, map_x]
}

function parseTuple(t) {
    return JSON.parse("[" + t.replace(/\(/g, "[").replace(/\)/g, "]") + "]")[0];
}