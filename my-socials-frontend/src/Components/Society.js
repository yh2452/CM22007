const Society = ({society}) => {
    return (
    <div> 
        <img src={society.imageUrl} alt="Society logo"/>
        <h4>{society.title}</h4>
    </div>
    )
}

export default Society