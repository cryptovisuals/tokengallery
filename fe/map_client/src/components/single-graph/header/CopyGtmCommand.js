import React, {Component} from 'react';
import {faClipboard} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

class CopyGtmCommand extends Component {

    constructor(props) {
        super(props);
        console.log(this.props.graph_metadata);
        this.copyGtmCommand = this.copyGtmCommand.bind(this)
        this.generateGtmCommand = this.generateGtmCommand.bind(this)
    }

    render() {
        return (

            <div className={'hover:cursor-pointer active:text-2xl ml-2'}
                 onClick={this.copyGtmCommand}>
                <p className={'mr-2'}>copy gtm command <FontAwesomeIcon
                    icon={faClipboard}/>
                </p>
            </div>

        );
    }

    copyGtmCommand() {
        let command = this.generateGtmCommand()
        navigator.clipboard.writeText(command);
    }

    generateGtmCommand() {
        let build = "./gtm.py" +
            " -n " + this.props.graph_metadata.graph_name +
            " --csv " + this.props.graph_metadata.source +
            " --ts " + this.props.graph_metadata.tile_size +
            " -z " + this.props.graph_metadata.zoom_levels +
            " --min_t " + this.props.graph_metadata.min_transparency +
            " --max_t " + this.props.graph_metadata.max_transparency +
            " --std " + this.props.graph_metadata.std_transparency_as_percentage +
            " --med_thick " + this.props.graph_metadata.med_edge_thickness +
            " --max_thick " + this.props.graph_metadata.max_edge_thickness +
            " --med_size " + this.props.graph_metadata.med_vertex_size +
            " --max_size " + this.props.graph_metadata.max_vertex_size +
            " --curvature " + this.props.graph_metadata.curvature +
            " --mean_t  " + this.props.graph_metadata.tile_based_mean_transparency +
            " --labels " + this.props.graph_metadata.labels
        return build;
    }
}

export default CopyGtmCommand;