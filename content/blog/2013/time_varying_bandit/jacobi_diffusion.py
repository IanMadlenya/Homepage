from pylab import *
from scipy.integrate import odeint
from scipy.stats import norm, uniform, beta

a = 0.0
b = 3.0
theta=1.0
sigma=sqrt(theta/(2*(a+b+2)))

def eigenvalue(n):
    return theta*n*(n+a+b+1)/(a+b+2)

gaussian_var = norm()
def dW(dt):
    return norm.rvs() / sqrt(dt)

def random_walk(y0, tmax, dt, times = None):
    def rhs(y,t):
        return -theta*(y-(a-b)/(a+b+2)) + sqrt(2*theta*(1-y*y)/(a+b+2))*dW(dt)
    if (times is None):
        times = arange(0,tmax,dt)
    y = zeros(shape=times.shape, dtype=float)
    y[0] = y0
    for i in range(1,y.shape[0]):
        y[i] = y[i-1] + rhs(y[i-1], times[i])*dt
        if abs(y[i]) > 1:
            y[i] = y[i] / abs(y[i])
    return (times, y)

N = 1000
x = zeros(shape=(N,), dtype=float)
t = None
tmax = 10
axis([0,tmax,0,1])
for i in range(N):
    t, y = random_walk(0.25, tmax, 0.01, t)
    x[i] = y[-1]
    if (i < 3):
        plot(t, (y+1)/2.0)

xlabel("time")
ylabel("CTR")
savefig("random_walk.png")

clf()
subplot(211)
hist((x+1)/2, bins=50)
ylabel("Monte carlo results")

subplot(212)
best_fit = beta.fit((x+1)/2, floc=0, fscale=1)

print best_fit
ctr = arange(0,1,0.001)
plot(ctr, beta(1,4).pdf(ctr), label="Invariant distribution, beta(1,4)")
plot(ctr, beta(best_fit[0],best_fit[1]).pdf(ctr), label="Best fit, beta("+str(best_fit[0]) + "," + str(best_fit[1]) + ")")
xlabel("CTR at t="+str(tmax))
ylabel("pdf")
legend()
savefig("long_term_random_walk_result.png")
