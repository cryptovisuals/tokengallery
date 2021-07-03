import React, {Component} from 'react';
import {bool, array, string} from "prop-types";
import AddableTag from "./AddableTag";

class Autocompletion extends Component {

    constructor(props) {
        super(props);
        this.state = {
            availableStrings: [],
        }
    }

    async componentDidMount() {
        let available_types = this.props.vertices_metadata.map(rec => rec['type']);
        let no_duplicates = Array.from(new Set(available_types));
        this.setState({availableStrings: no_duplicates})
    }


    render() {
        let regex = new RegExp('.*' + this.props.current_input.toLowerCase() + '.*');
        const matchedStrings = this.state.availableStrings.filter(s => s.toLowerCase().match(regex));


        return (
            matchedStrings.length > 0 && this.props.visible ?
                <div className={'relative z-50'}>
                    <div
                        className={'border-black border-2 p-2 flex flex-col absolute top-0 left-0 ml-1 bg-gray-100 w-48 h-48 overflow-y-auto'}>
                        {this.props.recentTags.map((str, i) => <AddableTag
                            key={i}
                            tag={str}
                            addTagCallback={this.props.addTagCallback}
                            bg_color={'bg-green-100'}/>)}
                        {matchedStrings.map((str, i) => <AddableTag
                            key={i + 5}
                            tag={str}
                            addTagCallback={this.props.addTagCallback}/>
                        )}
                    </div>
                </div> :
                <div/>
        )
            ;
    }
}

Autocompletion.propTypes = {
    current_input: string.isRequired,
    graph_name: string.isRequired,
    visible: bool.isRequired,
    vertices_metadata: array.isRequired
};

Autocompletion.defaultProps = {
    current_input: ''
};


export default Autocompletion;