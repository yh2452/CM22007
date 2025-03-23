const Event = ({eventPost}) => {
    onclick = {
        
    }
    return (
    <div> 
        <div>
            <h2>{eventPost.title}</h2>
            <h3>{eventPost.society}</h3>
        </div>
        <h3>{`${eventPost.date} ${eventPost.time} ${eventPost.location}`}</h3>
        <p>{eventPost.description}</p>
    </div>
    )
}

export default Event