import welcome_svg from '../assets/ilstrs/welcome.svg'
import {Link, useNavigate} from 'react-router-dom'
import {useLogin} from '../adapters/auth'
import {useState} from 'react'
import {notEmptyString} from '../utils'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
import '../styles/auth.css'
import {add_message} from '../store/messages'
import {useDispatch} from 'react-redux'
import {uid} from '../utils'

const Login=()=>{
    const login = useLogin()
    const [email , setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isLoading, setIsLoading]= useState(false)
    const dispatch = useDispatch()

    const nav = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        if(isLoading){
            return
        }
        if(notEmptyString(email) && notEmptyString(password)){
            setIsLoading(true)
            const res = await login(email, password)
            if(res.success){
                nav('/feed')
            }else{
                dispatch(add_message({type:'error', text:'Login failed, incorrect username or password', id:uid()}))
            }
            setIsLoading(false)
        }
    }

    return (
        <div>
        <Navbar />
        <main className='auth__main'>
            <section className='hidden md:block auth__ilstrWrapper'>
                <div className='w-3/4'>
                    <img src={welcome_svg} alt='Welcome'/>
                </div>
            </section>

            <section className='md:auth__formWrapper'>
                <h1 className='text-3xl'>Welcome back!</h1>
                <small className='text-xs'>Login to your account</small>
                <form className='auth__form' onSubmit={handleSubmit}>
                    <div className='my-4'>
                        <label htmlFor='email'>Email</label><br/>
                        <input type='email' required={true} value={email} onChange={(e)=> setEmail(e.target.value)}/>
                    </div>
                    <div className='my-4'>
                        <label htmlFor='password'>Password</label><br/>
                        <input type='password' required={true} value={password} onChange={(e)=> setPassword(e.target.value)}/>
                    </div>
                    <div>
                        <small className='my-5'>Forgot your password? <Link to='/password-reset'>Reset your password</Link></small>
                        <button className={isLoading ? 'auth__btn auth__btn--loading' : 'auth__btn'}>{isLoading ? 'Loading...' : 'Login'}</button>
                    </div>
                </form>
                <p  className='text-sm my-5'>Don't have an account? <Link to='/signup'>Signup</Link></p>
            </section>
        </main>
        <Footer/>
        </div>
    )
}
export default Login